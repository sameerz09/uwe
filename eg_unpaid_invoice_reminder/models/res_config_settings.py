from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _name = "res.config.settings"
    _inherit = "res.config.settings"

    unpaid_invoice_reminder = fields.Boolean(string="Unpaid Invoice Reminder")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        icpSudo = self.env["ir.config_parameter"].sudo()
        res.update(unpaid_invoice_reminder=icpSudo.get_param("eg_unpaid_invoice_reminder.unpaid_invoice_reminder"))
        return res

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        icpSudo = self.env["ir.config_parameter"].sudo()
        icpSudo.set_param("eg_unpaid_invoice_reminder.unpaid_invoice_reminder", self.unpaid_invoice_reminder)
        return res
