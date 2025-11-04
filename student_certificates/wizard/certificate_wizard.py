# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CertificateWizard(models.TransientModel):
    _name = 'student.certificate.wizard'
    _description = 'Student Certificate Wizard'

    student_id = fields.Many2one('university.student', string='Student', required=True)
    certificate_template = fields.Selection([
        ('registration', 'Registration Certificate'),
        ('completion', 'Completion Certificate'),
        ('achievement', 'Achievement Certificate'),
        ('enrollment', 'Enrollment Certificate'),
        ('custom', 'Custom Message'),
    ], string='Certificate Template', default='registration', required=True,
       help="Select the certificate template/message type")
    custom_certificate_message = fields.Html(string='Custom Certificate Message', 
                                             help="Custom message to display on certificate (only used when Custom Message is selected)")
    
    @api.model
    def default_get(self, fields_list):
        """Set default student from context"""
        res = super().default_get(fields_list)
        if 'default_student_id' in self.env.context:
            res['student_id'] = self.env.context['default_student_id']
            # Pre-fill with student's current template if exists
            student = self.env['university.student'].browse(res['student_id'])
            if student.exists():
                res['certificate_template'] = student.certificate_template or 'registration'
                res['custom_certificate_message'] = student.custom_certificate_message or ''
        return res

    def action_print_certificate(self):
        """Print certificate with selected template"""
        self.ensure_one()
        
        # Temporarily set the template on the student record
        original_template = self.student_id.certificate_template
        original_custom = self.student_id.custom_certificate_message
        
        self.student_id.certificate_template = self.certificate_template
        if self.certificate_template == 'custom':
            self.student_id.custom_certificate_message = self.custom_certificate_message
        
        try:
            # Get the certificate report
            report_ref = 'student_certificates.student_registration_certificate_report'
            report = self.env.ref(report_ref, raise_if_not_found=False)
            if not report:
                raise UserError(_("Certificate report not found. Please configure the certificate report."))
            
            # Return print action
            return report.report_action(self.student_id)
        finally:
            # Restore original values
            self.student_id.certificate_template = original_template
            if self.certificate_template == 'custom':
                self.student_id.custom_certificate_message = original_custom

    def action_send_certificate(self):
        """Send certificate via email with selected template"""
        self.ensure_one()
        
        # Temporarily set the template on the student record
        original_template = self.student_id.certificate_template
        original_custom = self.student_id.custom_certificate_message
        
        self.student_id.certificate_template = self.certificate_template
        if self.certificate_template == 'custom':
            self.student_id.custom_certificate_message = self.custom_certificate_message
        
        try:
            # Use the student's send certificate method
            return self.student_id.action_send_certificate()
        finally:
            # Restore original values
            self.student_id.certificate_template = original_template
            if self.certificate_template == 'custom':
                self.student_id.custom_certificate_message = original_custom

