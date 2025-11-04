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
from odoo.exceptions import UserError
import base64


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

    def action_send_payslip(self):
        """Send payslip to employee via email with PDF attachment"""
        self.ensure_one()
        
        # Check if employee has email
        if not self.employee_id.work_email and not self.employee_id.private_email:
            raise UserError(_("Employee %s does not have an email address configured.") % self.employee_id.name)
        
        # Get employee email
        employee_email = self.employee_id.work_email or self.employee_id.private_email
        
        # Get the payslip report - try different possible report references
        report_ref = None
        possible_refs = [
            'hr_payroll.action_report_payslip',
            'hr_payroll.report_payslip',
            'hr_payroll.report_hr_payslip',
        ]
        
        for ref in possible_refs:
            try:
                report = self.env.ref(ref, raise_if_not_found=False)
                if report:
                    report_ref = ref
                    break
            except:
                continue
        
        if not report_ref:
            # Fallback: search for payslip report by name
            report = self.env['ir.actions.report'].search([
                ('model', '=', 'hr.payslip'),
                ('report_type', '=', 'qweb-pdf')
            ], limit=1)
            if not report:
                raise UserError(_("Payslip report not found. Please configure the payslip report."))
            report_ref = report.report_name
        
        try:
            # Generate PDF for the payslip
            pdf_data = self.env['ir.actions.report']._render_qweb_pdf(
                report_ref, res_ids=self.ids
            )
            if not pdf_data or not pdf_data[0]:
                raise UserError(_("Failed to generate payslip PDF."))
            
            # Encode PDF data
            pdf_base64 = base64.b64encode(pdf_data[0]).decode()
            
            # Prepare email content
            payslip_name = self.number or f"Payslip-{self.employee_id.name}-{self.date_from.strftime('%Y-%m') if self.date_from else ''}"
            subject = _("Payslip - %s - %s") % (self.employee_id.name, payslip_name)
            
            body_html = _("""
                <p>Dear %s,</p>
                <p>Please find attached your payslip for the period %s to %s.</p>
                <p>Best regards,<br/>%s</p>
            """) % (
                self.employee_id.name,
                self.date_from.strftime('%B %d, %Y') if self.date_from else '',
                self.date_to.strftime('%B %d, %Y') if self.date_to else '',
                self.env.company.name
            )
            
            # Create email values
            email_values = {
                'subject': subject,
                'body_html': body_html,
                'email_from': self.env.company.email or self.env.user.email_formatted,
                'email_to': employee_email,
                'attachment_ids': [(0, 0, {
                    'name': f"{payslip_name}.pdf",
                    'type': 'binary',
                    'datas': pdf_base64,
                    'mimetype': 'application/pdf',
                    'res_model': 'hr.payslip',
                    'res_id': self.id,
                })],
            }
            
            # Create and send the email
            mail = self.env['mail.mail'].create(email_values)
            mail.send()
            
            # Log the action
            message = _("Payslip sent to %s (%s)") % (self.employee_id.name, employee_email)
            self.message_post(body=message)
            
            # Return notification
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Payslip Sent'),
                    'message': _('Payslip has been successfully sent to %s') % employee_email,
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            raise UserError(_("Error sending payslip: %s") % str(e))
