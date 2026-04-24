# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class UweSignDocument(models.Model):
    _name = 'uwe.sign.document'
    _description = 'UWE Sign Document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char('Document Name', required=True, tracking=True)
    ref = fields.Char('Reference', readonly=True, copy=False)
    employee_id = fields.Many2one('hr.employee', 'Employee', tracking=True)
    partner_id = fields.Many2one(
        'res.partner', 'Signatory',
        compute='_compute_partner_id', store=True, readonly=False,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Signature'),
        ('signed', 'Signed'),
        ('refused', 'Refused'),
    ], default='draft', string='Status', tracking=True)

    signature = fields.Binary('Signature', attachment=True)
    signed_by = fields.Char('Signed By', readonly=True)
    signed_date = fields.Datetime('Signed Date', readonly=True)
    document_content = fields.Html('Document Content')
    attachment_ids = fields.Many2many(
        'ir.attachment', string='Attachments',
        relation='uwe_sign_document_attachment_rel',
    )

    @api.depends('employee_id')
    def _compute_partner_id(self):
        for rec in self:
            if rec.employee_id and rec.employee_id.user_id:
                rec.partner_id = rec.employee_id.user_id.partner_id
            elif rec.employee_id and rec.employee_id.address_home_id:
                rec.partner_id = rec.employee_id.address_home_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('ref'):
                vals['ref'] = self.env['ir.sequence'].next_by_code('uwe.sign.document') or '/'
        return super().create(vals_list)

    def action_send_for_signature(self):
        for rec in self:
            if not rec.employee_id and not rec.partner_id:
                raise UserError(_('Please set an employee or signatory before sending.'))
            rec.state = 'waiting'

    def action_reset_to_draft(self):
        self.write({'state': 'draft', 'signature': False, 'signed_by': False, 'signed_date': False})

    def action_refuse(self):
        self.write({'state': 'refused'})

    def get_portal_url(self):
        self.ensure_one()
        return f'/my/sign/{self.id}'
