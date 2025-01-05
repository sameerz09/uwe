from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    unsubscribe_send_unpaid_invoice_mail = fields.Boolean(string="Un-Subscribe Send Unpaid Invoice Mail")