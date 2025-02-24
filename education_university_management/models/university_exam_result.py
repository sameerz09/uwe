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
    semester_date = fields.Date(string="Semester Date", required=True,
                       help="Select date of attendance")
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')],
                             default='draft', help="Status of attendance")
    subject_id = fields.Many2one('university.subject', string="Subject", required=True,
                                 help="Subject for the attendance")
    university_exam_result_line_ids = fields.One2many('university.exam.result.line', 'exam_result_id', string='Exam Result Line', help="Exam Result Line")
    is_degree_result_created = fields.Boolean(string='Degree Result Created',
                                           help="Is Degree Result created or not")
    
    def action_exam_result_done(self):
        self.state = 'done'

    def action_create_degree_result_line(self):
        if not self.university_exam_result_line_ids:
            raise UserError(_('There are no exam results in this table'))

        subject_title = self.subject_id.name
        subject_code = self.subject_id.code
        semester_date = self.semester_date

        for row in self.university_exam_result_line_ids:
            student = row.student_id
            if not student:
                raise UserError(_('Student information is missing for some records.'))

            # Create the degree result line
            degree_line = self.env["university.degree.result.line"].create({
                'course_code': subject_code,
                'course_title': subject_title,
                'total_marks': row.total_marks,
                'unit1': row.unit1,
                'unit2': row.unit2,
                'percentage': row.percentage,
                'grade': row.grade,
            })

            # Check if a semester record exists for the student
            semester = self.env["university.degree.result"].search([
                ("student_id", "=", student.id),
                ("semester_date", "=", semester_date)
            ], limit=1)

            if semester:
                semester.write({'courses_results': [(4, degree_line.id)]})
            else:
                self.env["university.degree.result"].create({
                    'student_id': student.id,
                    'semester_date': semester_date,
                    'courses_results': [(4, degree_line.id)],
                })

        self.is_degree_result_created = True
