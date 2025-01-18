from odoo import fields, models, api
import logging
_logger = logging.getLogger(__name__)


class StudentFeesLine(models.Model):
    _name = 'student.fees.line'

    fee_type_id = fields.Many2one('fee.type', string='Fee',
                                  required=True, help="Select fee types")
    is_registraion_fees = fields.Boolean(related='fee_type_id.is_registraion_fees',
                                         string='Registration Fees', readonly=True)
    # fee_description = fields.Text('Description', help="Fee type "
    #                                                   "description",
    #                               related='fee_type_id.description_sale')

    fee_description = fields.Text(
        string='Description',
        help="Fee type description"
    )
    due_amount = fields.Float('Due Amount', help="Due amount of the fee type")
    student_fees_id = fields.Many2one('student.fees', string='Student Fees')
    due_date = fields.Date('Due Date', help="Due date of the fee type")

    @api.model
    def update_fee_descriptions(self):
        _logger.info("Scheduled Action: Updating fee descriptions.")
        records = self.search([])
        for student_fees in records.mapped('student_fees_id'):  # Group by student fees
            fee_lines = student_fees.student_fees_line_ids.sorted('id')  # Sort fee lines by ID
            sequence = 0
            for line in fee_lines:
                if line.is_registraion_fees:
                    line.fee_description = "Registration Fees"
                else:
                    sequence += 1
                    line.fee_description = str(sequence)  # Assign sequential numbers
        _logger.info("Fee descriptions updated for all records.")