# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author:Jumana Jabin MP (odoo@cybrosys.com)
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
from odoo import fields, models, _


class UniversityAttendanceLine(models.Model):
    """For recording if the student is present during the day or not."""
    _name = 'university.attendance.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Attendance Lines'

    name = fields.Char(string='Name', help="Name of the attendance")
    attendance_id = fields.Many2one('university.attendance', string='Attendance Id', help="Relation field to attendance module")
    subject_id = fields.Many2one(related='attendance_id.subject_id', string='Subject', help="Subject for the attendance")
    student_id = fields.Many2one('university.student',
                                 string='Student',
                                 help="Students of the batch")
    student_no = fields.Char(related='student_id.student_no', string='Student Number', help="Student number")
    student_last_name = fields.Char(related='student_id.last_name', string='Last Name', help="Last name of the student")
    is_present_morning = fields.Boolean(string='Morning',
                                        help="Is student is present in the "
                                             "morning")
    is_present_afternoon = fields.Boolean(string='After Noon',
                                          help="Is student is present in "
                                               "the afternoon")
    full_day_absent = fields.Integer(string='Full Day',
                                     help="Is student full day absent or not ")
    half_day_absent = fields.Integer(string='Half Day',
                                     help="Is student half day absent or not ")
    batch_id = fields.Many2one('university.batch', string="Batch",
                               required=True,
                               help="Select batch for the attendance")
    date = fields.Date(string='Date', required=True, help="Attendance date")
    attendance_type = fields.Selection([('present', 'Present'), ('late', 'Late'),('absent', 'Absent'), ('excused', 'Excused')], string='Attendance Status', default='present', required=True, help="Select the attendance type")

    def action_apsent_warning(self):

        # Search for students with more than 10 'absent' records
        student_absences = self.read_group(
            [('attendance_type', '=', 'absent')],
            ['student_id'],  # Group by student
            ['student_id']
        )

        # Filter students with absences > 10
        students_to_warn = [
            record for record in student_absences if record['student_id_count'] > 5
        ]

        for student in students_to_warn:
            student_id = student['student_id'][0]
            student_name = student['student_id'][1]
            email = self.env['university.student'].browse(student_id).email

            if not email:
                continue  # Skip students without an email

            mail_message = _(
                "<p>Hello <strong>{student_name}</strong>,</p>"
                "<p>We noticed that your attendance records show more than 5 absences.</p>"
                "<p>Please take immediate steps to address your attendance and avoid further issues.</p>"
                "<p>For more details, contact your batch or subject supervisor.</p>"
                "<p>Thanks,</p>"
                "<p>Your University</p>"
            ).format(student_name=student_name)

            values = {
                'model': 'university.student',
                'res_id': student_id,
                'subject': "Attendance Warning: Excessive Absences",
                'body': mail_message,
                'body_html': mail_message,
                'email_to': email,
            }

            self.env['mail.mail'].sudo().create(values).send()
