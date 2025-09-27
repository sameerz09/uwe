# -*- coding: utf-8 -*-
import base64
import io
import pandas as pd
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class PayrollImportWizard(models.TransientModel):
    _name = 'payroll.import.wizard'
    _description = 'Payroll Import Wizard'

    excel_file = fields.Binary(string='Excel File', required=True)
    file_name = fields.Char(string='File Name', readonly=True)
    import_result = fields.Text(string='Import Result', readonly=True)

    def action_import_payslips(self):
        self.ensure_one()
        
        if not self.excel_file:
            raise UserError(_("Please select an Excel file to import."))
        
        try:
            file_content = base64.b64decode(self.excel_file)
            df = pd.read_excel(io.BytesIO(file_content))
            
            created_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    employee = self.env['hr.employee'].search([
                        ('name', 'ilike', str(row.get('Employee Name', '')))
                    ], limit=1)
                    
                    if not employee:
                        errors.append(f"Row {index + 1}: Employee not found")
                        continue
                    
                    payslip_data = {
                        'employee_id': employee.id,
                        'date_from': pd.to_datetime(row.get('Date From')).date(),
                        'date_to': pd.to_datetime(row.get('Date To')).date(),
                        'state': 'draft',
                    }
                    
                    self.env['hr.payslip'].create(payslip_data)
                    created_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {index + 1}: {str(e)}")
                    continue
            
            result = f"Created: {created_count} payslips\n"
            if errors:
                result += f"Errors: {len(errors)}\n" + "\n".join(errors[:10])
            
            self.write({'import_result': result})
            
            return {
                'type': 'ir.actions.act_window',
                'name': _('Import Result'),
                'res_model': 'payroll.import.wizard',
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'new'
            }
            
        except Exception as e:
            raise UserError(_("Error importing payslips: %s") % str(e))
