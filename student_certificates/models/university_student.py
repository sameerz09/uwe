# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import base64


class UniversityStudent(models.Model):
    _inherit = 'university.student'

    # Certificate fields
    passport_number = fields.Char(string='Passport Number', help="Student passport number")
    emirati_id_number = fields.Char(string='Emirati ID Number', help="Student Emirati ID number")
    program_name = fields.Char(string='Study Program', default='Bachelor of Business Administration', 
                               help="Name of the study program")
    academic_year = fields.Char(string='Academic Year', help="Academic year (e.g., 2025/2026)")
    license_number = fields.Char(string='License Number', default='4308400.01', 
                                 help="License number for the program")
    full_name_english = fields.Char(string='Full Name (English)', 
                                    help="Full name of the student in English")
    full_name_arabic = fields.Char(string='Full Name (Arabic)', 
                                   help="Full name of the student in Arabic")
    visa_number = fields.Char(string='Visa Number', help="Student visa number")
    english_level_exam = fields.Char(string='English Level Exam', 
                                     help="English proficiency exam result (e.g., IELTS 7.0, TOEFL 90, etc.)")
    letter_to_students = fields.Html(string='Letter to Students', 
                                     help="Letter content for students")
    letter_to_employees = fields.Html(string='Letter to Employees', 
                                      help="Letter content for employees")
    # Attachment fields - one for each document type (Binary fields for direct upload)
    high_school_certificate_attachment = fields.Binary(string='High School Certificate',
                                                        help="Upload high school certificate file")
    high_school_certificate_filename = fields.Char(string='High School Certificate Filename')
    passport_attachment = fields.Binary(string='Passport Attachment',
                                       help="Upload passport document file")
    passport_filename = fields.Char(string='Passport Filename')
    visa_attachment = fields.Binary(string='Visa Attachment',
                                   help="Upload visa document file")
    visa_filename = fields.Char(string='Visa Filename')
    english_level_exam_attachment = fields.Binary(string='English Level Exam Attachment',
                                                  help="Upload English level exam document file")
    english_level_exam_filename = fields.Char(string='English Level Exam Filename')
    letter_to_students_attachment = fields.Binary(string='Letter to Students Attachment',
                                                  help="Upload letter to students file")
    letter_to_students_filename = fields.Char(string='Letter to Students Filename')
    letter_to_employees_attachment = fields.Binary(string='Letter to Employees Attachment',
                                                   help="Upload letter to employees file")
    letter_to_employees_filename = fields.Char(string='Letter to Employees Filename')
    certificate_template = fields.Selection([
        ('registration', 'Registration Certificate'),
        ('completion', 'Completion Certificate'),
        ('achievement', 'Achievement Certificate'),
        ('enrollment', 'Enrollment Certificate'),
        ('custom', 'Custom Message'),
    ], string='Certificate Template', default='registration', 
       help="Select the certificate template/message type")
    custom_certificate_message = fields.Html(string='Custom Certificate Message', 
                                             help="Custom message to display on certificate (only used when Custom Message is selected)")

    def action_send_certificate(self):
        """Send registration certificate to student via email with PDF attachment"""
        self.ensure_one()
        
        # Check if student has email
        if not self.email and not self.personal_email:
            raise UserError(_("Student %s does not have an email address configured.") % self.name)
        
        # Get student email
        student_email = self.email or self.personal_email
        
        # Get the certificate report
        report_ref = 'student_certificates.student_registration_certificate_report'
        try:
            report = self.env.ref(report_ref, raise_if_not_found=False)
            if not report:
                # Fallback: search for certificate report
                report = self.env['ir.actions.report'].search([
                    ('model', '=', 'university.student'),
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
            
            # Prepare email content based on template
            template_names = {
                'registration': _('Certificate of Registration'),
                'completion': _('Certificate of Completion'),
                'achievement': _('Certificate of Achievement'),
                'enrollment': _('Certificate of Enrollment'),
                'custom': _('Certificate'),
            }
            student_name = self.full_name_english or self.partner_id.name or self.name
            certificate_type = template_names.get(self.certificate_template, _('Certificate'))
            certificate_name = f"{certificate_type}-{student_name}"
            subject = _("%s - %s") % (certificate_type, student_name)
            
            body_html = _("""
                <p>Dear %s,</p>
                <p>Please find attached your %s.</p>
                <p>Best regards,<br/>%s</p>
            """) % (
                student_name,
                certificate_type,
                self.env.company.name
            )
            
            # Create email values
            email_values = {
                'subject': subject,
                'body_html': body_html,
                'email_from': self.env.company.email or self.env.user.email_formatted,
                'email_to': student_email,
                'attachment_ids': [(0, 0, {
                    'name': f"{certificate_name}.pdf",
                    'type': 'binary',
                    'datas': pdf_base64,
                    'mimetype': 'application/pdf',
                    'res_model': 'university.student',
                    'res_id': self.id,
                })],
            }
            
            # Create and send the email
            mail = self.env['mail.mail'].create(email_values)
            mail.send()
            
            # Log the action
            message = _("Certificate sent to %s (%s)") % (self.name, student_email)
            self.message_post(body=message)
            
            # Return notification
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Certificate Sent'),
                    'message': _('Certificate has been successfully sent to %s') % student_email,
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            raise UserError(_("Error sending certificate: %s") % str(e))

