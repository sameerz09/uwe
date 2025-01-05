import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.model_create_multi
    def create(self, vals_list):
        payments = super(AccountPayment, self).create(vals_list)

        for vals, payment in zip(vals_list, payments):
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
                        f"This student's fees have a payment. The highest name is '{payment.highest_name}' "
                        f"and the amount is {vals.get('amount')}."
                    )
                    if vals.get('ref'):
                        message += f" The invoice reference is '{vals.get('ref')}'."

                    # Add log note to the first draft student fee record
                    student_fees[0].add_log_note(message)

        return payments
