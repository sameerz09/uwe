from odoo import models, fields, api
from datetime import datetime


class HrContract(models.Model):
    _inherit = 'hr.contract'

    wage_usd = fields.Float(string='Wage USD')
    wage_egp = fields.Float(string='Wage EGP')

    @api.onchange('wage_usd')
    def _onchange_wage_usd(self):
        # get the exchange rate from the company
        usd_currency_id = self.env['res.currency'].search([('name', '=', 'USD')]).id
        exchange_rate = self.env['res.currency']._get_conversion_rate(self.env['res.currency'].browse(usd_currency_id), self.currency_id, self.env.company, datetime.now())
        if exchange_rate:
            self.wage = self.wage_usd * exchange_rate

    @api.onchange('wage_egp')
    def _onchange_wage_egp(self):
        # get the exchange rate from the company
        egp_currency_id = self.env['res.currency'].search([('name', '=', 'EGP')]).id
        exchange_rate = self.env['res.currency']._get_conversion_rate(self.env['res.currency'].browse(egp_currency_id), self.currency_id, self.env.company, datetime.now())
        if exchange_rate:
            self.wage = self.wage_egp * exchange_rate