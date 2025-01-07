import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.model_create_multi
    def create(self, vals):
        payments = super(AccountPayment, self).create(vals)

        for vals, payment in zip(vals, payments):
            partner_id = vals.get('partner_id')
            if partner_id:
                partner = self.env['res.partner'].browse(partner_id)
                student_fees = self.env['student.fees'].search([
                    ('student_no', '=', partner.student_no),
                    ('state', '=', 'draft')
                ])

                if student_fees:
                    # Construct the log message
                    message = (
                        f"This student's fees have a payment at '{payment.write_date}' "
                        f"and the amount is {vals.get('amount')}."
                    )
                    if vals.get('ref'):
                        move_id = self.env['account.move'].search([('payment_reference', '=', vals.get('ref'))])
                        message += f" The invoice reference is '{vals.get('ref')}'."
                        if move_id.invoice_date_due:
                          message += f" The due invoice date is '{move_id.invoice_date_due}'."

                    # Add log note to the first draft student fee record
                    student_fees[0].add_log_note(message)

        return payments
