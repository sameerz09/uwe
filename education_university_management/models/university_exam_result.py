from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class UniversityExamResult(models.Model):
    _name='university.exam.result'
    _description='Exam Result'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string="Name", default="New",
                       help="Name of the exam result")
    
    batch_id = fields.Many2one('university.batch', string="Batch",
                               required=True,
                               help="Select batch for the attendance")
    date = fields.Date(string="Date", default=fields.Date.today, required=True,
                       help="Select date of attendance")
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')],
                             default='draft', help="Status of attendance")
    subject_id = fields.Many2one('university.subject', string="Subject", required=True,
                                 help="Subject for the attendance")
    university_exam_result_line_ids = fields.One2many('university.exam.result.line', 'exam_result_id', string='Exam Result Line', help="Exam Result Line")
    is_exam_result_created = fields.Boolean(string='Exam Result Created',
                                           help="Is Exam Result created or not")
    
    def action_exam_result_done(self):
        self.state = 'done'


    def action_create_exam_result_line(self):
        if self.search_count([('batch_id', '=', self.batch_id.id), ('date', '=', self.date),('state', '=', 'done')]) == 1:
            raise ValidationError(
                _('Attendance for this batch on this date already exists.'))
        self.name = str(self.date)
        if len(self.batch_id.batch_student_ids) < 1:
            raise UserError(_('There are no students in this Batch'))
        for student in self.batch_id.batch_student_ids:
            self.env['university.exam.result.line'].create(
                {
                 'exam_result_id': self.id,
                 'student_id': student.id,
                })
        self.is_exam_result_created = True