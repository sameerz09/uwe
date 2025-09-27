# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    employee_department = fields.Char(
        string='Department',
        related='employee_id.department_id.name',
        store=True,
        readonly=True
    )
    
    employee_job = fields.Char(
        string='Job Position',
        related='employee_id.job_id.name',
        store=True,
        readonly=True
    )
    
    net_wage_display = fields.Float(
        string='Net Wage',
        compute='_compute_net_wage_display',
        store=True
    )

    @api.depends('line_ids', 'line_ids.total')
    def _compute_net_wage_display(self):
        for payslip in self:
            net_line = payslip.line_ids.filtered(lambda l: l.code == 'NET')
            payslip.net_wage_display = net_line.total if net_line else 0.0