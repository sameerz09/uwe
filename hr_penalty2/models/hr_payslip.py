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
from odoo import api, models, _


class HrPayslip(models.Model):
    """ This class is used to create the bonus reasons. """
    _inherit = "hr.payslip"

    def compute_sheet(self):
        """Override compute_sheet to auto-fill number_of_hours from contract's total_working_hours"""
        # Call the original compute_sheet method first
        result = super(HrPayslip, self).compute_sheet()
        
        # Auto-fill number_of_hours from contract's total_working_hours
        for payslip in self:
            if payslip.contract_id and payslip.contract_id.total_working_hours:
                total_working_hours = payslip.contract_id.total_working_hours
                
                # Update number_of_hours in worked_days_line_ids
                # Find the Attendance line (common codes: WORK100, ATTENDANCE, or name contains 'Attendance')
                for worked_day_line in payslip.worked_days_line_ids:
                    # Check if it's an attendance type line
                    if worked_day_line.code in ['WORK100', 'ATTENDANCE', 'ATT'] or \
                       'Attendance' in (worked_day_line.name or '') or \
                       worked_day_line.work_entry_type_id.code in ['WORK100', 'ATTENDANCE']:
                        # Update number_of_hours with contract's total_working_hours
                        worked_day_line.number_of_hours = total_working_hours
        
        return result

    @api.onchange('employee_id', 'date','struct_id')
    def _onchange_employee_id(self):
        """ When changing teacher attendance the bonus amount for the employee will be
        loaded as other input  """
        # Only proceed if struct_id exists
        if not self.struct_id:
            return
        
        rules = self.struct_id.rule_ids.mapped('name')
        
        # Try to get attendance rule - handle if it doesn't exist
        try:
            attendance_rule = self.env.ref('hr_penalty.hr_salary_rule_attendance')
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
        except ValueError:
            # Salary rule doesn't exist, skip attendance processing
            pass
        
        # Try to get penalty rule - handle if it doesn't exist
        try:
            penalty_rule = self.env.ref('hr_penalty.hr_salary_rule_penalty')
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
        except ValueError:
            # Salary rule doesn't exist, skip penalty processing
            pass
