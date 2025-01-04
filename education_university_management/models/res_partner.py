# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Jumana Jabin MP (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from odoo import fields, models, api


class ResPartner(models.Model):
    """Inherited model for adding two fields to determine
                    whether the partner student or parent"""
    _inherit = 'res.partner'

    is_student = fields.Boolean(string="Is a Student",
                                help="Enable if the partner is a student")
    is_parent = fields.Boolean(string="Is a Parent",
                               help="Enable if the partner is a parent")
    student_no = fields.Char(string="Student Number", help="Student Number", compute='_compute_student_no', readonly=True)

    def _compute_student_no(self):
        for rec in self:
            student_id = self.env['university.student'].search([('partner_id', '=', rec.id)], limit=1)
            if student_id:
                rec.student_no = student_id.student_no
            else:
                rec.student_no = False

    
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = rec.name
            if rec.student_no:
                rec.display_name = rec.display_name + ' - ' + rec.student_no

    def get_student_name(self):
        for rec in self:
            student_id = self.env['university.student'].search([('partner_id', '=', rec.id)], limit=1)
            if student_id:
                studen_name = student_id.name
                if student_id.middle_name:
                    studen_name = studen_name + ' ' + student_id.middle_name
                if student_id.last_name:
                    studen_name = studen_name + ' ' + student_id.last_name
                return studen_name
            else:
                return False


    # @api.model
    # def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
    #     domain = domain or []
    #     if name:
    #         # Be sure name_search is symetric to display_name
    #         name = name.split(' / ')[-1]
    #         domain = ['|', ('student_no', operator, name), ('name', operator, name)] + domain
    #     return self._search(domain, limit=limit, order=order)