

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class UniversityDegreeResultLine(models.Model):
    _name = 'university.degree.result.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Degree Results Lines'

    degree_result_id = fields.Many2one(
        'university.degree.result',
        string='Degree Result Id',
        help="Relation field to Degree result module"
    )

    course_code = fields.Char(
        string='Course Code',
        help="Course Code"
    )
    course_title = fields.Char(
        string='Course Title',
        help="Course Title"
    )
    total_marks = fields.Float(string='Total Marks')
    unit1 = fields.Float(string='Unit 1', default=0)
    unit2 = fields.Float(string='Unit 2', default=0)
    percentage = fields.Char(string="Percentage", default="")
    grade = fields.Char(string="Grade", default="")
