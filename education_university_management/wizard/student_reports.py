
from odoo import fields, models


class StudentReports(models.TransientModel):

    _name = 'student.reports'
    _description = 'Student Reports'

    student_id = fields.Many2one('university.student',
                                       string="Student",
                                       help="Choose the student to make report for him")
    reports = fields.Selection(
        [
            ("marks", "Student  marks "),
            ("schedule ", "Schedule "),
            ("study_letter", "Study letter"),
        ],
        default="marks"

    )

    def generate_report(self):
        print("report1")


