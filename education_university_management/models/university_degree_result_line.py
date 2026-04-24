

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
    exam_result_id = fields.Many2one(
        'university.exam.result',
        string='Exam Result',
        help="Linked exam result record this line was imported from"
    )
    course_code = fields.Char(
        string='Course Code',
        help="Course Code"
    )
    course_title = fields.Char(
        string='Course Title',
        help="Course Title"
    )
    semester_date = fields.Date(string='Semester Date')
    total_marks = fields.Char(string='Total Marks')
    unit1 = fields.Float(string='Unit 1', default=0)
    unit2 = fields.Float(string='Unit 2', default=0)
    percentage = fields.Char(string="Percentage", default="")
    grade = fields.Char(string="Grade", default="")

    def action_open_exam_result(self):
        self.ensure_one()
        if not self.exam_result_id:
            raise UserError(_('No exam result linked to this line.'))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Exam Result'),
            'res_model': 'university.exam.result',
            'view_mode': 'form',
            'res_id': self.exam_result_id.id,
            'target': 'current',
        }
