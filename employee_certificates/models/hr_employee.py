# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import base64


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # Certificate fields
    passport_number = fields.Char(string='Passport Number', help="Employee passport number")
    emirati_id_number = fields.Char(string='Emirati ID Number', help="Employee Emirati ID number")
    program_name = fields.Char(string='Study Program', default='Bachelor of Business Administration', 
                               help="Name of the study program")
    academic_year = fields.Char(string='Academic Year', help="Academic year (e.g., 2025/2026)")
    license_number = fields.Char(string='License Number', default='4308400.01', 
                                 help="License number for the program")

    def action_send_certificate(self):
        """Send registration certificate to employee via email with PDF attachment"""
        self.ensure_one()
        
        # Check if employee has email
        if not self.work_email and not self.private_email:
            raise UserError(_("Employee %s does not have an email address configured.") % self.name)
        
        # Get employee email
        employee_email = self.work_email or self.private_email
        
        # Get the certificate report
        report_ref = 'employee_certificates.employee_registration_certificate_report'
        try:
            report = self.env.ref(report_ref, raise_if_not_found=False)
            if not report:
                # Fallback: search for certificate report
                report = self.env['ir.actions.report'].search([
                    ('model', '=', 'hr.employee'),
                    ('report_name', 'ilike', 'certificate'),
                    ('report_type', '=', 'qweb-pdf')
                ], limit=1)
                if not report:
                    raise UserError(_("Certificate report not found. Please configure the certificate report."))
                report_ref = report.report_name
        except:
            raise UserError(_("Certificate report not found. Please configure the certificate report."))
        
        try:
            # Generate PDF for the certificate
            pdf_data = self.env['ir.actions.report']._render_qweb_pdf(
                report_ref, res_ids=self.ids
            )
            if not pdf_data or not pdf_data[0]:
                raise UserError(_("Failed to generate certificate PDF."))
            
            # Encode PDF data
            pdf_base64 = base64.b64encode(pdf_data[0]).decode()
            
            # Prepare email content
            certificate_name = f"Certificate-{self.name}"
            subject = _("Certificate of Student Registration - %s") % self.name
            
            body_html = _("""
                <p>Dear %s,</p>
                <p>Please find attached your Certificate of Student Registration in a study program.</p>
                <p>Best regards,<br/>%s</p>
            """) % (
                self.name,
                self.env.company.name
            )
            
            # Create email values
            email_values = {
                'subject': subject,
                'body_html': body_html,
                'email_from': self.env.company.email or self.env.user.email_formatted,
                'email_to': employee_email,
                'attachment_ids': [(0, 0, {
                    'name': f"{certificate_name}.pdf",
                    'type': 'binary',
                    'datas': pdf_base64,
                    'mimetype': 'application/pdf',
                    'res_model': 'hr.employee',
                    'res_id': self.id,
                })],
            }
            
            # Create and send the email
            mail = self.env['mail.mail'].create(email_values)
            mail.send()
            
            # Log the action
            message = _("Certificate sent to %s (%s)") % (self.name, employee_email)
            self.message_post(body=message)
            
            # Return notification
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Certificate Sent'),
                    'message': _('Certificate has been successfully sent to %s') % employee_email,
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            raise UserError(_("Error sending certificate: %s") % str(e))

