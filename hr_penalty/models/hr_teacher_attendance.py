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


class HrTeacherAttendance(models.Model):
    _name = "hr.teacher.attendance"
    _inherit = ['mail.thread']


    name = fields.Char(string="Name", readonly=True, store=True)
    employee_id = fields.Many2one('hr.employee', required= True ,string='Employee', )
    course_id = fields.Many2one('university.course',required= True, string='Course Name', )
    date = fields.Date(string='Lecture Date', default=fields.Date.context_today,required= True,
                                 tracking=5)
    no_hours = fields.Integer(string="No of hours",required= True, store=True)
    amount = fields.Float(string="Amount", required=True, store=True)
    struct_id = fields.Many2one('hr.payroll.structure',
                                string='Salary Structure',
                                help="Choose Payroll Structure",store=True)
    contract_id = fields.Many2one('hr.contract',
                                string='Contract',store=True,
                                help="Choose Payroll Structure")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approved'),
    ], string="State", default='draft', tracking=5, copy=False)

    @api.onchange('employee_id')
    def _onchange_employee(self):
        if self.employee_id:
            values = self.env['hr.contract'].search(
                [('employee_id', '=', self.employee_id.id)],limit=1)
            print('@@@@@@@@@@@@@@@@@@@@@',values)
            self.contract_id = values.id
            self.struct_id = values.struct_id



    def action_approve(self):
        if self.no_hours:
            self.amount = self.no_hours *self.contract_id.amount_hour
        self.write({'state': 'approve'})


class HrContract(models.Model):
    _inherit = ['hr.contract']

    amount_hour = fields.Float("Amount Per Hour")

#     @api.model
#     def create(self, vals):
#         """ Override the create function for creating new sequence number.
#         @params vals (dict): values for creating new records.
#         @returns res (models.Model): the created records of 'bonus.request' """
#         if vals.get('reference', 'New') == 'New':
#             vals['reference'] = self.env['ir.sequence'].next_by_code(
#                 'hr.penalty') or 'New'
#         res = super(HrTeacherAttendance, self).create(vals)
#         return res
#
#
#
#
# class HrContract(models.Model):
#     _inherit = 'hr.contract'
#
#     # attendance_ids = fields.One2many('', 'employee_id', string='last_penalty',
#     #                               domain=[('state', '=', 'approve')])
#     penalty_count = fields.Integer(compute='_compute_penalty_count', string='Penalty Count')
#
#     # def _compute_penalty_count(self):
#     #     """
#     #     A method to count all employees penalty without repetition.
#     #     """
#     #     penalty_data = self.env['hr.penalty'].sudo().read_group([('employee_id', '=', self.id)], ['employee_id'],
#     #                                                             ['employee_id'])
#     #     result = dict((data['employee_id'][0], data['employee_id_count']) for data in penalty_data)
#     #     for employee in self:
#     #         employee.penalty_count = result.get(employee.id, 0)
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
#     penailty_name = fields.Char('Penalty')

