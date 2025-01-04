from odoo import fields, models, api


class StudentFeesLine(models.Model):
    _name = 'student.fees.line'

    fee_type_id = fields.Many2one('fee.type', string='Fee',
                                  required=True, help="Select fee types")
    is_registraion_fees = fields.Boolean(related='fee_type_id.is_registraion_fees',
                                         string='Registration Fees', readonly=True)
    fee_description = fields.Text('Description', help="Fee type "
                                                      "description",
                                  related='fee_type_id.description_sale')
    due_amount = fields.Float('Due Amount', help="Due amount of the fee type")
    student_fees_id = fields.Many2one('student.fees', string='Student Fees')
    due_date = fields.Date('Due Date', help="Due date of the fee type")