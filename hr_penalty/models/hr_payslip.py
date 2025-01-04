# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Sabeel B (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from odoo import api, models


class HrPayslip(models.Model):
    """ This class is used to create the bonus reasons. """
    _inherit = "hr.payslip"

    @api.onchange('employee_id', 'date','struct_id')
    def _onchange_employee_id(self):
        """ When changing teacher attendance the bonus amount for the employee will be
        loaded as other input  """
        attendance_rule = self.env.ref(
            'hr_penalty.hr_salary_rule_attendance')
        rules = self.struct_id.rule_ids.mapped('name')
        if attendance_rule.name in rules:
            attendance = self.env['hr.teacher.attendance'].search([
                ('employee_id', '=', self.employee_id.id),
                ('state', '=', 'approve'),
                ('date', '>=', self.date_from),])

            amount = sum(attendance.mapped('amount'))
            print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',attendance)
            self.input_line_ids = [(0, 0, {
                'name': 'Attendance',
                'code': 'ATT',
                'contract_id': self.contract_id.id,
                'amount': amount,
            })]
        penalty_rule = self.env.ref(
            'hr_penalty.hr_salary_rule_penalty')
        penalty_rules = self.struct_id.rule_ids.mapped('name')
        if penalty_rule.name in penalty_rules:
            penalty_attendance = self.env['hr.penalty'].search([
                ('employee_id', '=', self.employee_id.id),
                ('state', '=', 'posted'),
                ('violation_date', '>=', self.date_from),
                ('violation_date', '<=', self.date_to)])
            penalty_amount = sum(penalty_attendance.mapped('deduct_amount'))
            print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@', penalty_attendance)
            self.input_line_ids = [(0, 0, {
                'name': 'Penalty',
                'code': 'PEN',
                'contract_id': self.contract_id.id,
                'amount': penalty_amount,
            })]
