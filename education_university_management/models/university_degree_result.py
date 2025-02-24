from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class UniversityDegreeResult(models.Model):
    _name = 'university.degree.result'
    _description = 'Degree Result'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    student_id = fields.Many2one(
        'university.student',
        string='Student',
        help="Student associated with the degree result",
        required=True
    )

    semester_date = fields.Date(string="Semester Date",  required=True,
                       help="Select date of semester")

    gpa = fields.Float(String="GPA")
    cumulative_gpa = fields.Float(String="Cumulative GPA")
    courses_results = fields.One2many(
        'university.degree.result.line','degree_result_id',
        string='Degree Results Lines',
        help="Degree Results Lines associated with the degree result"
    )