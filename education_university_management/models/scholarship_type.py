from odoo import fields, models


class ScholarshipType(models.Model):
    _name = 'scholarship.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Scholarship Types"

    name = fields.Char('Name', required=True,
                       help="Enter the name of scholarship type")
    description = fields.Text(string="Description",
                              help="Any additional information about scholarship")
    percentage = fields.Float(string="Percentage",  required=True,
                              help="Percentage of scholarship")
    