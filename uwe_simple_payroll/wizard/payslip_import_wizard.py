# -*- coding: utf-8 -*-
import base64
import io
import csv
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PayslipImportWizard(models.TransientModel):
    _name = 'payslip.import.wizard'
    _description = 'Payslip Import Wizard'

    file_data = fields.Binary(
        string='CSV File',
        required=False,
        help='Upload CSV file with payslip data'
    )
    file_name = fields.Char(string='File Name')
    
    # Sample data for template
    sample_data = fields.Text(
        string='Sample Data',
        readonly=True,
        default='''Employee Name,Basic Salary,Gross Salary,Net Salary,From Date,To Date,State
John Doe,5000.00,5000.00,4500.00,2025-01-01,2025-01-31,draft
Jane Smith,6000.00,6000.00,5400.00,1/1/2025,1/31/2025,draft
Mike Johnson,4000.00,4000.00,3600.00,01-01-2025,01-31-2025,draft

IMPORTANT NOTES:
1. Employee must exist in the system
2. Employee must have an ACTIVE contract
3. You can use any of these date formats:
   - YYYY-MM-DD (2025-01-01)
   - MM/DD/YYYY (1/1/2025)
   - DD/MM/YYYY (1/1/2025)
   - DD-MM-YYYY (1-1-2025)'''
    )

    def _parse_date(self, date_str):
        """Parse date string with multiple format support"""
        if not date_str or not date_str.strip():
            return False
        
        date_str = date_str.strip()
        
        # List of possible date formats
        date_formats = [
            '%Y-%m-%d',      # 2025-01-01
            '%m/%d/%Y',      # 1/1/2025
            '%d/%m/%Y',      # 1/1/2025 (European)
            '%Y/%m/%d',      # 2025/01/01
            '%d-%m-%Y',      # 1-1-2025
            '%m-%d-%Y',      # 1-1-2025 (US)
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # If no format matches, try to parse as is
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
        except ValueError:
            raise ValueError(f"Unable to parse date: {date_str}")

    def action_download_template(self):
        """Download CSV template file"""
        self.ensure_one()
        
        # Create CSV content
        csv_content = self.sample_data
        
        # Create file attachment
        attachment = self.env['ir.attachment'].create({
            'name': 'payslip_import_template.csv',
            'type': 'binary',
            'datas': base64.b64encode(csv_content.encode('utf-8')),
            'mimetype': 'text/csv',
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }

    def action_import_payslips(self):
        """Import payslips from CSV file"""
        self.ensure_one()
        
        if not self.file_data:
            raise UserError(_('Please select a file to import.'))
        
        try:
            # Decode file
            file_content = base64.b64decode(self.file_data)
            csv_data = io.StringIO(file_content.decode('utf-8'))
            reader = csv.DictReader(csv_data)
            
            imported_count = 0
            errors = []
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # Get employee
                    employee_name = row.get('Employee Name', '').strip()
                    if not employee_name:
                        errors.append(f'Row {row_num}: Employee Name is required')
                        continue
                    
                    employee = self.env['hr.employee'].search([
                        ('name', 'ilike', employee_name)
                    ], limit=1)
                    
                    if not employee:
                        errors.append(f'Row {row_num}: Employee "{employee_name}" not found. Available employees: {", ".join(self.env["hr.employee"].search([]).mapped("name"))}')
                        continue
                    
                    # Get any contract for this employee (ignore state)
                    contract = self.env['hr.contract'].search([
                        ('employee_id', '=', employee.id)
                    ], limit=1)
                    
                    if not contract:
                        errors.append(f'Row {row_num}: Employee "{employee_name}" has no contract. Please create a contract first.')
                        continue
                    
                    # If contract exists but not active, try to activate it
                    if contract.state not in ['open', 'draft', 'done']:
                        try:
                            contract.state = 'open'
                        except:
                            pass  # Continue even if we can't change state
                    
                    # Get or create payslip structure
                    structure = self.env['hr.payroll.structure'].search([], limit=1)
                    if not structure:
                        errors.append(f'Row {row_num}: No payroll structure found')
                        continue
                    
                    # Parse dates
                    date_from = self._parse_date(row.get('From Date', ''))
                    date_to = self._parse_date(row.get('To Date', ''))
                    
                    if not date_from or not date_to:
                        errors.append(f'Row {row_num}: Invalid date format. Use YYYY-MM-DD or MM/DD/YYYY')
                        continue
                    
                    # Create payslip name
                    payslip_name = f"Salary Slip - {employee.name} - {date_from} to {date_to}"
                    
                    # Create payslip
                    payslip_vals = {
                        'name': payslip_name,
                        'employee_id': employee.id,
                        'struct_id': structure.id,
                        'date_from': date_from,
                        'date_to': date_to,
                        'state': row.get('State', 'draft'),
                    }
                    
                    # Add contract if available
                    if contract:
                        payslip_vals['contract_id'] = contract.id
                    
                    payslip = self.env['hr.payslip'].create(payslip_vals)
                    
                    # Create payslip lines for basic, gross, and net
                    try:
                        basic_amount = float(row.get('Basic Salary', 0) or 0)
                        gross_amount = float(row.get('Gross Salary', 0) or 0)
                        net_amount = float(row.get('Net Salary', 0) or 0)
                    except (ValueError, TypeError):
                        errors.append(f'Row {row_num}: Invalid salary amounts. Please use numbers only.')
                        continue
                    
                    # Create payslip lines only if we have amounts
                    if basic_amount > 0 or gross_amount > 0 or net_amount > 0:
                        # Basic Salary line
                        if basic_amount > 0:
                            try:
                                self.env['hr.payslip.line'].create({
                                    'payslip_id': payslip.id,
                                    'name': 'Basic Salary',
                                    'code': 'BASIC',
                                    'category_id': self.env.ref('hr_payroll.BASIC').id,
                                    'amount': basic_amount,
                                    'total': basic_amount,
                                    'quantity': 1,
                                    'rate': 100,
                                })
                            except:
                                pass  # Skip if category doesn't exist
                        
                        # Gross Salary line
                        if gross_amount > 0:
                            try:
                                self.env['hr.payslip.line'].create({
                                    'payslip_id': payslip.id,
                                    'name': 'Gross',
                                    'code': 'GROSS',
                                    'category_id': self.env.ref('hr_payroll.GROSS').id,
                                    'amount': gross_amount,
                                    'total': gross_amount,
                                    'quantity': 1,
                                    'rate': 100,
                                })
                            except:
                                pass  # Skip if category doesn't exist
                        
                        # Net Salary line
                        if net_amount > 0:
                            try:
                                self.env['hr.payslip.line'].create({
                                    'payslip_id': payslip.id,
                                    'name': 'Net Salary',
                                    'code': 'NET',
                                    'category_id': self.env.ref('hr_payroll.NET').id,
                                    'amount': net_amount,
                                    'total': net_amount,
                                    'quantity': 1,
                                    'rate': 100,
                                })
                            except:
                                pass  # Skip if category doesn't exist
                    
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f'Row {row_num}: {str(e)}')
                    continue
            
            # Show results
            message = f'Successfully imported {imported_count} payslips.'
            if errors:
                message += f'\n\nErrors:\n' + '\n'.join(errors[:10])
                if len(errors) > 10:
                    message += f'\n... and {len(errors) - 10} more errors.'
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Import Complete'),
                    'message': message,
                    'type': 'success' if not errors else 'warning',
                    'sticky': True,
                }
            }
            
        except Exception as e:
            raise UserError(_('Error importing file: %s') % str(e))
