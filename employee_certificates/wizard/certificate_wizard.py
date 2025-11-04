# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class EmployeeCertificateWizard(models.TransientModel):
    _name = 'employee.certificate.wizard'
    _description = 'Employee Certificate Wizard'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
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
        """Set default employee from context"""
        res = super().default_get(fields_list)
        if 'default_employee_id' in self.env.context:
            res['employee_id'] = self.env.context['default_employee_id']
            # Pre-fill with employee's current template if exists
            employee = self.env['hr.employee'].browse(res['employee_id'])
            if employee.exists():
                res['certificate_template'] = employee.certificate_template or 'registration'
                res['custom_certificate_message'] = employee.custom_certificate_message or ''
        return res

    def action_print_certificate(self):
        """Print certificate with selected template"""
        self.ensure_one()
        
        # Temporarily set the template on the employee record
        original_template = self.employee_id.certificate_template
        original_custom = self.employee_id.custom_certificate_message
        
        self.employee_id.certificate_template = self.certificate_template
        if self.certificate_template == 'custom':
            self.employee_id.custom_certificate_message = self.custom_certificate_message
        
        try:
            # Get the certificate report
            report_ref = 'employee_certificates.employee_registration_certificate_report'
            report = self.env.ref(report_ref, raise_if_not_found=False)
            if not report:
                raise UserError(_("Certificate report not found. Please configure the certificate report."))
            
            # Return print action
            return report.report_action(self.employee_id)
        finally:
            # Restore original values
            self.employee_id.certificate_template = original_template
            if self.certificate_template == 'custom':
                self.employee_id.custom_certificate_message = original_custom

    def action_send_certificate(self):
        """Send certificate via email with selected template"""
        self.ensure_one()
        
        # Temporarily set the template on the employee record
        original_template = self.employee_id.certificate_template
        original_custom = self.employee_id.custom_certificate_message
        
        self.employee_id.certificate_template = self.certificate_template
        if self.certificate_template == 'custom':
            self.employee_id.custom_certificate_message = self.custom_certificate_message
        
        try:
            # Use the employee's send certificate method
            return self.employee_id.action_send_certificate()
        finally:
            # Restore original values
            self.employee_id.certificate_template = original_template
            if self.certificate_template == 'custom':
                self.employee_id.custom_certificate_message = original_custom

