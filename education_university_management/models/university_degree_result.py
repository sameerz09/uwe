from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import base64

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

    def action_fill_student_marks(self):
        """Fill courses_results by searching exam result lines directly by student_no."""
        self.ensure_one()
        if not self.student_id:
            raise UserError(_('Please select a student before filling marks.'))
        if not self.semester_date:
            raise UserError(_('Please select a semester date before filling marks.'))

        student_no = self.student_id.student_no
        student_id = self.student_id.id

        # Find all exam result lines for this student where
        # the exam semester_date is on or before this degree result's semester_date
        student_filter = ['|',
            ('student_no', '=', student_no),
            ('student_id', '=', student_id),
        ] if student_no else [('student_id', '=', student_id)]

        domain = student_filter + [
            ('exam_result_id.semester_date', '=', self.semester_date),
        ]

        exam_lines = self.env['university.exam.result.line'].search(domain)

        if not exam_lines:
            raise UserError(_(
                'No exam result lines found for student "%s" (No: %s) '
                'with semester date %s.\n'
                'Please ensure exam results have been entered for this student and semester.'
            ) % (self.student_id.name, student_no or 'N/A', self.semester_date))

        # Delete all existing lines and recreate from scratch
        self.courses_results.unlink()

        lines_to_create = []
        seen_codes = set()

        for line in exam_lines:
            exam = line.exam_result_id
            if not exam or not exam.subject_id:
                continue

            course_code = exam.subject_id.code or ''

            if course_code in seen_codes:
                continue

            lines_to_create.append({
                'degree_result_id': self.id,
                'exam_result_id': exam.id,
                'semester_date': exam.semester_date,
                'course_code': course_code,
                'course_title': exam.subject_id.name or '',
                'total_marks': line.total_marks or '0',
                'unit1': line.unit1,
                'unit2': line.unit2,
                'percentage': line.percentage or '',
                'grade': line.grade or '',
            })
            seen_codes.add(course_code)

        if not lines_to_create:
            raise UserError(_(
                'No subjects could be matched for student "%s".'
            ) % self.student_id.name)

        self.env['university.degree.result.line'].create(lines_to_create)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Marks Filled'),
                'message': _('%d course(s) loaded successfully.') % len(lines_to_create),
                'type': 'success',
                'sticky': False,
            },
        }

    def action_send_degree(self):
        """
        Generate a single report for multiple records and send an email to the student.
        """
        # Ensure there are records selected
        if not self:
            raise UserError("No records selected!")

        # Get the first student (assuming all selected records belong to the same student)
        student = self[0].student_id
        if not student.email:
            raise UserError(f"Student {student.name} does not have an email address!")

        # Get the report reference
        report_ref = 'university_degree.University_result'
        report = self.env['ir.actions.report']._get_report(report_ref)
        if not report:
            raise UserError(f"Report '{report_ref}' not found!")

        # Generate the report for all selected records
        report_data = self.env['ir.actions.report']._render_qweb_pdf(report_ref, res_ids=self.ids)

        # Prepare email values
        email_values = {
            'subject': f"Degree Report for {student.name}",
            'body_html': f"""
                <p>Dear {student.name} {student.last_name},</p>
                <p>Please find attached your degree.</p>
                <p>Best regards,<br/>University Administration</p>
            """,
            'email_to': student.email,
            'attachment_ids': [(0, 0, {
                'name': f"Degree_Report_{student.name}.pdf",
                'type': 'binary',
                'datas': base64.b64encode(report_data[0]).decode(),
            })],
        }

        # Send the email
        self.env['mail.mail'].create(email_values).send()

        # Log the action
        message = f"Degree report sent to {student.name} ({student.email})."
        self[0].message_post(body=message)
