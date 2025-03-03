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

    gpa = fields.Float(
        string="GPA",
        compute="_compute_gpa",
        store=True,
        default="0.0"
    )

    cumulative_gpa = fields.Float(
        string="Cumulative GPA",
        compute="_compute_cumulative_gpa",
        store=True,
        default="0.0"
    )
    courses_results = fields.One2many(
        'university.degree.result.line','degree_result_id',
        string='Degree Results Lines',
        help="Degree Results Lines associated with the degree result"
    )

    @api.depends("courses_results")
    def _compute_gpa(self):
        for rec in self:
            total_mark = 0
            mark_num = 0
            for line in rec.courses_results:
                if line.total_marks != 'Eq':
                    try:
                        total_mark += float(line.total_marks)  # Use float to avoid conversion errors
                        mark_num += 1
                    except ValueError:
                        continue  # Skip invalid values

            if mark_num > 0:
                rec.gpa = ((total_mark / mark_num) / 100) * 4

    @api.depends("gpa")
    def _compute_cumulative_gpa(self):
        for rec in self:
            if not rec.student_id:
                rec.cumulative_gpa = 0.0
                continue

            semesters = self.env["university.degree.result"].search([("student_id", "=", rec.student_id.id)])

            total_gpa = 0
            gpa_num = 0

            for semester in semesters:
                if semester.gpa != 0.0:
                    try:
                        total_gpa += float(semester.gpa)  # Use float to avoid conversion errors
                        gpa_num += 1
                    except ValueError:
                        continue  # Skip invalid values
            for semester in semesters:
                semester.cumulative_gpa = total_gpa / gpa_num if gpa_num > 0 else 0.0
            rec.cumulative_gpa = total_gpa / gpa_num if gpa_num > 0 else 0.0


    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['university.degree.result'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'university.degree.result',
            'docs': docs,
        }