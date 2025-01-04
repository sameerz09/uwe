from odoo import api, fields, models, _


class UniversityExamResultLine(models.Model):
    _name = 'university.exam.result.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Exam Results Lines'

    exam_result_id = fields.Many2one('university.exam.result',
                                    string='exam result Id',
                                    help="Relation field to exam result module")
    student_id = fields.Many2one('university.student',
                                 string='Student',
                                 help="Students of the batch")
    total_marks = fields.Float(string='Total Marks')
    student_no = fields.Char(related='student_id.student_no', string='Student Number', help="Student number")
    student_last_name = fields.Char(related='student_id.last_name', string='Last Name', help="Last name of the student")
    student_passed_state = fields.Selection([('passed', 'Passed'), ('not_passed', 'Not Passed')], string='Passed', default='not_passed',
                                      help="Is Student Passed or not", force_save=True)
    

    @api.onchange('total_marks')
    def onchange_total_marks(self):
        if self.total_marks >= self.exam_result_id.subject_id.pass_mark:
            self.student_passed_state = 'passed'
        else:
            self.student_passed_state = 'not_passed'