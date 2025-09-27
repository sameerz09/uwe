# -*- coding: utf-8 -*-
import base64
import io
import pandas as pd
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class PayrollExportWizard(models.TransientModel):
    _name = 'payroll.export.wizard'
    _description = 'Payroll Export Wizard'

    export_type = fields.Selection([
        ('selected', 'Selected Payslips'),
        ('all', 'All Payslips'),
    ], string='Export Type', default='selected', required=True)
    
    payslip_ids = fields.Many2many('hr.payslip', string='Payslips to Export')
    file_name = fields.Char(string='File Name', default='payslips_export.xlsx', required=True)
    excel_file = fields.Binary(string='Excel File', readonly=True)

    def action_export_excel(self):
        self.ensure_one()
        payslips = self.payslip_ids if self.export_type == 'selected' else self.env['hr.payslip'].search([])
        
        if not payslips:
            raise UserError(_("No payslips found to export."))
        
        data = []
        for payslip in payslips:
            data.append({
                'Employee Name': payslip.employee_id.name,
                'Employee ID': payslip.employee_id.employee_id,
                'Department': payslip.employee_department or '',
                'Job Position': payslip.employee_job or '',
                'Payslip Number': payslip.number or '',
                'Date From': payslip.date_from.strftime('%Y-%m-%d') if payslip.date_from else '',
                'Date To': payslip.date_to.strftime('%Y-%m-%d') if payslip.date_to else '',
                'State': payslip.state,
                'Net Wage': payslip.net_wage_display,
            })
        
        df = pd.DataFrame(data)
        excel_data = df.to_excel(index=False)
        
        self.write({
            'excel_file': base64.b64encode(excel_data),
            'file_name': self.file_name
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content?model=payroll.export.wizard&id={self.id}&field=excel_file&filename_field=file_name&download=true',
            'target': 'new'
        }
