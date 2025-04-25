# from odoo import api, fields, models, _
# from odoo.exceptions import UserError
#
# class UniversityExamResultLine(models.Model):
#     _name = 'university.exam.result.line'
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#     _description = 'Exam Results Lines'
#
#     exam_result_id = fields.Many2one('university.exam.result',
#                                     string='exam result Id',
#                                     help="Relation field to exam result module")
#     student_id = fields.Many2one('university.student',
#                                  string='Student',
#                                  help="Students of the batch", compute="_compute_student_infos", store=True)
#     total_marks = fields.Float(string='Total Marks')
#     # student_no = fields.Char(related='student_id.student_no', string='Student Number', help="Student number")
#     # student_last_name = fields.Char(related='student_id.last_name', string='Last Name', help="Last name of the student")
#     # student_last_name = fields.Char(string='Last Name', help="Last name of the student")
#     student_no = fields.Char(string='Student Number', help="Student number")
#     student_first_name = fields.Char(string='First Name', help="First name of the student", compute="_compute_student_infos", store=True)
#     student_last_name = fields.Char(string='Last Name', help="Last name of the student", compute="_compute_student_infos", store=True)
#
#     student_passed_state = fields.Selection([('passed', 'Passed'), ('not_passed', 'Not Passed')], string='Passed', default='not_passed',
#                                       help="Is Student Passed or not", force_save=True)
#     unit1 = fields.Float(string='Unit', default=0)
#     unit2 = fields.Float(string='Unit', default=0)
#     percentage = fields.Char(string="Percentage", default="")
#     grade = fields.Char(string="Grade", default=0)
#
#
#     @api.onchange('total_marks')
#     def onchange_total_marks(self):
#         if self.total_marks >= self.exam_result_id.subject_id.pass_mark:
#             self.student_passed_state = 'passed'
#         else:
#             self.student_passed_state = 'not_passed'
#
#     @api.depends('student_no')
#     def _compute_student_infos(self):
#         for rec in self:
#             if self.student_no:
#                 student = self.env["university.student"].search[("student_no", "=", self.student_no)]
#                 if student:
#                     rec.student_id = student
#                     rec.student_first_name = student.first_name
#                     rec.student_last_name = student.last_name
#                 else:
#                     raise UserError('Please check the students numbers and ensure that this studen is exist')
#             else:
#                 raise UserError('Please check the students numbers ')


from odoo import api, fields, models, _
from odoo.exceptions import UserError


class UniversityExamResultLine(models.Model):
    _name = 'university.exam.result.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Exam Results Lines'

    exam_result_id = fields.Many2one(
        'university.exam.result',
        string='Exam Result Id',
        help="Relation field to exam result module"
    )

    student_id = fields.Many2one(
        'university.student',
        string='Student',
        help="Student associated with the exam result"
    )

    total_marks = fields.Char(string='Total Marks')

    student_no = fields.Char(
        string='Student Number',
        help="Student number", required=True
    )

    student_first_name = fields.Char(
        string='First Name',
        help="First name of the student",
        compute="_compute_student_infos",
        store=True
    )

    student_last_name = fields.Char(
        string='Last Name',
        help="Last name of the student",
        compute="_compute_student_infos",
        store=True
    )

    student_passed_state = fields.Selection(
        [('passed', 'Passed'), ('not_passed', 'Not Passed')],
        string='Passed',
        default='not_passed',
        help="Indicates if the student has passed or not",
        tracking=True
    )

    unit1 = fields.Float(string='Unit 1', default=0)
    unit2 = fields.Float(string='Unit 2', default=0)
    percentage = fields.Char(string="Percentage", default="")
    grade = fields.Char(string="Grade", default="")

    @api.depends('student_no')
    def _compute_student_infos(self):
        for rec in self:
            if rec.student_no:
                student = self.env["university.student"].search([("student_no", "=", rec.student_no)], limit=1)
                if student:
                    rec.student_id = student
                    rec.student_first_name = student.first_name
                    rec.student_last_name = student.last_name
                else:
                    raise UserError("please check the Stduent Numbers and ensure the sudent is exist")
            else:
                return UserError("please check the Stduent Numbers ")

    @api.onchange('total_marks')
    def onchange_total_marks(self):
        for rec in self:
            if rec.exam_result_id and rec.exam_result_id.subject_id:
                pass_mark = rec.exam_result_id.subject_id.pass_mark
                rec.student_passed_state = 'passed' if rec.total_marks >= pass_mark else 'not_passed'
            else:
                rec.student_passed_state = 'not_passed'
