# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Jumana Jabin MP(odoo@cybrosys.com)
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


class FeeStructureLines(models.Model):
    _name = 'fee.structure.line'
    _description = "Fee Structure lines"

    fee_structure_id = fields.Many2one('fee.structure',
                                       help="Relation to fee.structure",
                                       string='Fee Structure',
                                       ondelete='cascade', index=True)
    category_id = fields.Many2one(related='fee_structure_id.category_id',
                                  string="Category",
                                  help="Fee category of structure")
    fee_type_id = fields.Many2one('fee.type', string='Fee',
                                  required=True, help="Select fee types")
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  default=lambda
                                      self: self.env.user.company_id.currency_id.id,
                                  help="Currency of current company")
    is_registraion_fees = fields.Boolean(related='fee_type_id.is_registraion_fees',
                                         string='Registration Fees', readonly=True)
    fee_amount = fields.Float('Amount Before Scholarship', required=True,
                              help="Amount of the each fee type",
                              related='fee_type_id.lst_price')
    # fee_amount = fields.Float('Amount Before Scholarship', required=True,
    #                           help="Amount of the each fee type")
    payment_type = fields.Selection(string='Payment Type',
                                    help="Payment type of fee type",
                                    related="fee_type_id.payment_type")
    fee_description = fields.Text('Description', help="Fee type "
                                                      "description",
                                  related='fee_type_id.description_sale')
    first_scholarship_id = fields.Many2one('scholarship.type', string='First Scholarship')
    second_scholarship_id = fields.Many2one('scholarship.type', string='Second Scholarship')
    due_amount = fields.Float('Due Amount', help="Due amount of the fee type", readonly=False, compute='_compute_due_amount')
    is_paid = fields.Boolean('Is Paid', help="To determine whether the fee type is paid or not", readonly=True)


    # @api.model
    # def create(self, vals):
    #     res = super(FeeStructureLines, self).create(vals)
    #     res.due_amount = res.fee_type_id.lst_price
    #     return res

    # @api.onchange('first_scholarship_id', 'second_scholarship_id')
    # def _onchange_first_scholarship_id(self):
    #     first_scholarship_percent = self.first_scholarship_id.percentage / 100
    #     second_scholarship_percent = self.second_scholarship_id.percentage / 100
    #     self.due_amount = self.fee_type_id.lst_price - (self.fee_type_id.lst_price * (first_scholarship_percent + second_scholarship_percent))

    def _compute_due_amount(self):
        for rec in self:
            if rec.is_registraion_fees:
                # إذا كانت رسوم تسجيل، خليه ياخذ المبلغ كامل بدون خصم
                rec.due_amount = rec.fee_type_id.lst_price
            else:
                first_scholarship_percent = rec.first_scholarship_id.percentage / 100
                second_scholarship_percent = rec.second_scholarship_id.percentage / 100
                rec.due_amount = rec.fee_type_id.lst_price - (
                        rec.fee_type_id.lst_price * (first_scholarship_percent + second_scholarship_percent)
                )
