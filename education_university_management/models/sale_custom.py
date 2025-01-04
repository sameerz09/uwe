# -*- coding: utf-8 -*-
###############################################################################
#
#    IATL-Intellisoft International Pvt. Ltd.
#    Copyright (C) 2021 Tech-Receptives(<http://www.iatl-intellisoft.com>).
#
###############################################################################

from odoo import api, fields, models, tools, _
# from odoo.exceptions import Warning
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime, time, timedelta
from odoo.tools.translate import html_translate


class Partner(models.Model):
    _inherit = ['res.partner']
    first_name = fields.Char(string="First Name", compute='_compute_fields')
    middle_name = fields.Char(string="Middle Name")
    last_name = fields.Char(string="Last Name", )
    Parent_tel = fields.Char(string="Reference Number", )

    @api.depends('name')
    def _compute_fields(self):
        for rec in self:
            if rec.name:
                rec.first_name = rec.name.split(' ')[0]
                # if rec.name.split(' ')[1]:
                #     rec.last_name = rec.name.split(' ')[1]
            else:
                rec.first_name = ' '



class SaleOrder(models.Model):
    _inherit = ['sale.order']

    application_id = fields.Many2one('university.application', string='Student Application', readonly=True)
    test = fields.Boolean(string='test',default=True)

    def action_create_application(self):
        """ Function for the 'Post Journal Entry' button to create a draft entry
         for approved deduct request """
        student_email = self.env['university.application'].search([('email', '=', self.partner_id.email)], limit=1)
        if student_email:
            raise UserError(_('Student already registered.'))
        else:
            student_application = self.env['university.application'].create({
                'title': self.partner_id.title or '',
                'name': self.partner_id.first_name,
                'last_name': self.partner_id.last_name or '',
                'state': 'draft',
                'email': self.partner_id.email,
                'mobile': self.partner_id.phone or '',
                'phone': self.partner_id.mobile or '',
                'city': self.partner_id.city or '',
                'street': self.partner_id.street or '',
                'sale_id' : self.id,
                'user_id' : self.user_id.id,
                'partner_id' : self.partner_id.id,
            })
            student_application.state = 'draft'
            self.application_id = student_application.id



    def action_view_application_form(self):
        return {
            'name': 'Application Form',
            'type': 'ir.actions.act_window',
            'res_model': 'university.application',
            'view_mode': 'form',
            'res_id': self.application_id.id
        }

#
#     @api.depends('employee_id')
#     def _compute_name(self):
#         employee_id = self.employee_id
#         if employee_id:
#             self.name = "Penalty For Employee " + employee_id.name
#     # new
#     @api.onchange('violation_config_id')
#     def onchange_violation(self):
#         violation_config_name = self.violation_config_id.id
#         print('############################################',violation_config_name)
#         if violation_config_name:
#             penalty_name = self.env['hr.penalty.config'].search([('id', '=', violation_config_name)],limit= 1)
#             self.penalty_config = penalty_name.penailty_name
#
#     @api.onchange('employee_id')
#     def onchange_employee_id(self):
#         employee_id = self.employee_id.id
#         if employee_id:
#             penalty_id = self.env['hr.penalty'].search([('employee_id', '=', employee_id)] ,limit=1,order ='violation_date desc')
#             self.last_penalty_id = penalty_id.penalty_config
#
#     name = fields.Char(string="Name", compute='_compute_name', readonly=True, store=True)
#     employee_id = fields.Many2one('hr.employee', string='Employee', )
#     violation_id = fields.Many2one('hr.violation', string="violation", tracking=5)
#     violation_date = fields.Date(string='Violation Date', default=fields.Date.context_today,
#                                  tracking=5)
#     amount = fields.Float(string='Amount')
#     last_penalty_id = fields.Many2one('hr.penalty', string='last_penalty', ondelete='set null', )
#     punishment_type = fields.Selection(selection=[
#         ('warning', 'Warning'),
#         ('penalty', 'Deduct'),
#         ('terminate', 'Terminate')],  string='Punishment Type',
#         default='warning')
#     state = fields.Selection([
#         ('draft', 'Draft'),
#         ('approve', 'HR Approved'),
#         ('accounting', 'Accounting'),
#         ('posted', 'Accounting ِApproved'),
#         ('reject', 'Reject'),
#     ], string="State", default='draft', tracking=5, copy=False)
#     company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
#     #service_termination_id = fields.Many2one('hr.service.termination', string='Servise Termination Ref')
#     violation_config_id = fields.Many2one('hr.penalty.config', string='Violation')
#     penalty_config =  fields.Char(string="Penalty", readonly=True, store=True)
#     confirming_employee_id = fields.Many2one('hr.employee', string='Confirming Employee')
#     approving_employee_id = fields.Many2one('hr.employee', string='Approving Employee')
#     reference = fields.Char(string='Reference Number', copy=False,
#                             help='Sequence number for the Penalty request.')
#     deduct_amount = fields.Float(string='Deduct Amount', tracking=True,
#                                 help='This amount will be deduct from salary.')
#     journal_id = fields.Many2one('account.journal', string='Journal',
#                                  help='The Jornal for Penalty request',
#                                  company_dependent=True, required=False,
#                                  domain="[('type', '=', 'general')]",
#                                  state={'accounting': [('required', True)]})
#     move_id = fields.Many2one('account.move', string='Accounting Entry',
#                               help='Accounting entry of penalty request',
#                               readonly=True)
#     credit_account_id = fields.Many2one('account.account',
#                                         string='Credit Account',
#                                         help='The credit account for creating '
#                                              'journal entry',
#                                         state={'accounting': [('required', True)]})
#     debit_account_id = fields.Many2one('account.account',
#                                        string='Debit Account',
#                                        help='The debit account for creating '
#                                             'journal entry',
#                                        state={'accounting': [('required', True)]})
#
#     @api.model
#     def create(self, vals):
#         """ Override the create function for creating new sequence number.
#         @params vals (dict): values for creating new records.
#         @returns res (models.Model): the created records of 'bonus.request' """
#         if vals.get('reference', 'New') == 'New':
#             vals['reference'] = self.env['ir.sequence'].next_by_code(
#                 'hr.penalty') or 'New'
#         res = super(HrPenalty, self).create(vals)
#         return res
#
#
#
#
#     def action_approve(self):
#         self.write({'state': 'approve'})
#
#     def action_accounting(self):
#         self.write({'state': 'accounting'})
#

#
#
#     def unlink(self):
#         """
#         A method to delete penalty in draft status
#         """
#         for order in self:
#             if order.state not in ('draft',):
#                 raise UserError(_('You can not delete record not in draft state.'))
#         return super(HrPenalty, self).unlink()
#
#     def action_mail_send(self):
#         # self.write({'state': 'sent'})
#
#         self.ensure_one()
#         ir_model_data = self.env['ir.model.data']
#         try:
#             template_id = ir_model_data.get_object_reference('hr_penalty', 'penalty_teamplate_id')[1]
#         except ValueError:
#             template_id = False
#
#         ctx = dict(self.env.context or {})
#         ctx.update({
#             'default_model': 'hr.penalty',
#             'default_res_id': self.ids[0],
#             'default_use_template': bool(template_id),
#             'default_template_id': template_id,
#             'default_composition_mode': 'comment',
#             'force_email': True
#         })
#
#         return {
#             'name': _('Penalty Email'),
#             'type': 'ir.actions.act_window',
#             'view_type': 'form',
#             'view_mode': 'form',
#             'res_model': 'mail.compose.message',
#             'target': 'new',
#             'context': ctx,
#         }
#
#
# class Employee(models.Model):
#     _inherit = 'hr.employee'
#
#     penalty_ids = fields.One2many('hr.penalty', 'employee_id', string='last_penalty',
#                                   domain=[('state', '=', 'approve')])
#     penalty_count = fields.Integer(compute='_compute_penalty_count', string='Penalty Count')
#
#     def _compute_penalty_count(self):
#         """
#         A method to count all employees penalty without repetition.
#         """
#         penalty_data = self.env['hr.penalty'].sudo().read_group([('employee_id', '=', self.id)], ['employee_id'],
#                                                                 ['employee_id'])
#         result = dict((data['employee_id'][0], data['employee_id_count']) for data in penalty_data)
#         for employee in self:
#             employee.penalty_count = result.get(employee.id, 0)
#
#
#
# class HrViolation(models.Model):
#     _name = 'hr.violation'
#
#     name = fields.Char('Name')
#
# class HrPenaltyConfig(models.Model):
#     _name = "hr.penalty.config"
#
#     @api.depends('rule_no')
#     def _compute_penalty(self):
#         rule_no = self.rule_no
#         if rule_no:
#             self.rule_name = "Rule NO " + rule_no
#
#     rule_name = fields.Char('Name',compute='_compute_penalty', readonly=True, store=True)
#     rule_no = fields.Char('Rule No')
#     name = fields.Char('Violation Name')
#    ئty_name = fields.Char('Penalty')
