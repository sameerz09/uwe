# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    portal_user_count = fields.Integer(
        string='Portal Users',
        compute='_compute_portal_user_count',
    )

    def _compute_portal_user_count(self):
        for partner in self:
            partner.portal_user_count = self.env['res.users'].sudo().search_count([
                ('partner_id', '=', partner.id),
            ])

    def action_open_portal_user(self):
        self.ensure_one()
        existing_user = self.env['res.users'].sudo().search([
            ('partner_id', '=', self.id),
        ], limit=1)

        if existing_user:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Portal User'),
                'res_model': 'res.users',
                'view_mode': 'form',
                'res_id': existing_user.id,
            }

        if not self.email:
            raise UserError(_('The contact must have an email address to create a portal user.'))

        new_user = self.env['res.users'].sudo().create({
            'name': self.name,
            'login': self.email,
            'partner_id': self.id,
            'user_type': 'portal',
        })

        return {
            'type': 'ir.actions.act_window',
            'name': _('Portal User'),
            'res_model': 'res.users',
            'view_mode': 'form',
            'res_id': new_user.id,
        }
