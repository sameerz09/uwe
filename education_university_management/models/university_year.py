from odoo import models, fields, api


class UniversityYear(models.Model):
    _name = 'university.year'
    _description = 'University Year'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Year', required=True)
    semster_ids = fields.One2many('university.semester', 'year_id', string='Semesters')
