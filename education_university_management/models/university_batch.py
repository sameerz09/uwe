# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Jumana Jabin MP (odoo@cybrosys.com)
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
from odoo import fields, models, api, _
from base64 import b64encode


class UniversityBatch(models.Model):
    """For managing batches of every department in the university"""
    _name = 'university.batch'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "University Batches"

    @api.model
    def create(self, vals):
        """Return the name as a str of semester + academic year"""
        semester_id = self.env['university.semester'].browse(
            vals['semester_id'])
        academic_year_id = self.env['university.academic.year'].browse(
            vals['academic_year_id'])
        department_id = self.env['university.department'].browse(
            vals['department_id'])
        # name = str(department_id.code + ' - ' + semester_id.name + ' - ' + academic_year_id.name)
        name = str( academic_year_id.name + ' - ' + department_id.code +  ' - ' + str(semester_id.semester_no) )
        vals['name'] = name
        return super(UniversityBatch, self).create(vals)

    name = fields.Char(string="Name", help="Name of the Batch", readonly=True)
    semester_id = fields.Many2one('university.semester',
                                  string="Semester", required=True,
                                  help="Select the semester")
    # department_id = fields.Many2one(related='semester_id.department_id',
    #                                 string="Department",
    #                                 help="In which department this "
    #                                      "batch belongs to")
    department_id = fields.Many2one('university.department', string="Department", required=True)
    timetable_id = fields.Many2one('university.timetable', string="Timetable", required=True)
    email_sender_id = fields.Many2one('ir.mail_server', string="Email Sender", required=True)
    academic_year_id = fields.Many2one('university.academic.year',
                                       string="Academic Year", required=True,
                                       help="Select the academic year")
    batch_strength = fields.Integer(string='Batch Strength',
                                    help="Total strength of the batch")
    faculty_id = fields.Many2one('university.faculty',
                                 string='Faculty', help="Batch tutor/Faculty")
    batch_student_ids = fields.One2many('university.student',
                                        'batch_id',
                                        string="Students",
                                        help="Students of this Batch")
    year_id = fields.Many2one('university.year', string="Year", required=True)
    timetable_report = fields.Binary(string="Timetable Report", readonly=True)
    timetable_report_name = fields.Char(string="Report Filename", readonly=True)


    def action_open_attendance_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Attendance Report Wizard',
            'res_model': 'attendance.report.wizard',
            'view_mode': 'form',
            'target': 'new',
        }


    def action_send_mail(self):
        """Generate timetable report and send it via email to all students in the batch."""
        self.ensure_one()

        # Fetch the report action
        report_service = self.env.ref('education_university_management.report_timetable')
        if not report_service:
            raise ValueError("Timetable report action is not defined.")

        # Generate the PDF report
        pdf_data, x = self.env['ir.actions.report'].sudo()._render_qweb_pdf(
            'education_university_management.report_timetable', [self.timetable_id.id]
        )
        if not pdf_data:
            raise ValueError("Failed to generate the timetable report.")

        # Encode the PDF data as base64
        encoded_pdf = b64encode(pdf_data)

        # Set the filename for the PDF
        file_name = f"{self.name}_Timetable_Report.pdf"

        for student in self.batch_student_ids:
            if not student.email:
                continue  # Skip if the student does not have an email

            # Compose the email body

            mail_message = _(
                "<p>Hello <strong>_person_name_</strong>,</p>"
                "<p>Please find your timetable attached to this email.</p>"
                "<p>Thanks,</p>"
                "<p>The University Team</p>"
            )
            mail_message = mail_message.replace("_person_name_", student.name or "Student")

            # mail_message = _(
            #     "<p>Hello <strong>{name}</strong>,</p>"
            #     "<p>Please find your timetable attached to this email.</p>"
            #     "<p>Thanks,</p>"
            #     "<p>The University Team</p>"
            # ).format(name=student.name or "Student")

            # Prepare email values
            values = {
                'subject': f"Timetable for {self.name}",
                'body_html': mail_message,
                'email_from': self.email_sender_id.smtp_user,
                'email_to': student.email,
                'attachment_ids': [(0, 0, {
                    'name': file_name,
                    'type': 'binary',
                    'datas': encoded_pdf,
                    'mimetype': 'application/pdf',
                })],
            }

            # Create and send the email
            self.env['mail.mail'].sudo().create(values).send()
