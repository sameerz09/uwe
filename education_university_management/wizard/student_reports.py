
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
            ("withdraw_form", "Withdraw Form"),
        ],
        default="marks"

    )

    def generate_report(self):

        vals = {
            'student_id': self.student_id.id,
        }
        # Create the wizard record with the report data


        if self.reports == "marks":
            res = self.env['student.marks'].create(vals)
            return self.env.ref('education_university_management.action_student_marks_report').report_action(res)
        elif self.reports == "schedule":
            pass

        elif self.reports == "study_letter":
            res = self.env['student.letter'].create(vals)
            return self.env.ref('education_university_management.action_study_letter_report').report_action(res)

        elif self.reports == "withdraw_form":
            res = self.env['withdraw.form'].create(vals)
            return self.env.ref('education_university_management.action_withdraw_form_report').report_action(res)





class StudentsMarks(models.TransientModel):
    _name = 'student.marks'
    _description = 'Student Marks'

    student_id = fields.Many2one('university.student',
                                 string="Student",
                                 help="Choose the student to make report for him")


class StudyLetter(models.TransientModel):
    _name = 'student.letter'
    _description = 'Student Letter'

    student_id = fields.Many2one('university.student',
                                 string="Student",
                                 help="Choose the student to make report for him")

class WithdrawForm(models.TransientModel):
    _name = 'withdraw.form'
    _description = 'Withdraw Form'

    student_id = fields.Many2one('university.student',
                                 string="Student",
                                 help="Choose the student to make report for him")

