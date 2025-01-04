from odoo import fields, models


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    def _get_payment_terminal_selection(self):
        return super(PosPaymentMethod, self)._get_payment_terminal_selection() + [('neoleap', 'Neoleap')]

    neoleap_terminal_ip = fields.Char('Neoleap Terminal IP')
