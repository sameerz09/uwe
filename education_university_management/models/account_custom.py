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


class AccountPayment(models.Model):
    _inherit = ['account.payment']

    paid = fields.Boolean('Paid')


class AccountMove(models.Model):
    _inherit = ['account.move']

    def _cron_fetch_unpaid_student(self, limit=None):
        date_now = fields.Date.today()
        print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%',date_now)
        paid_invoices = self.search(
            [('state', '=', 'posted'), ('payment_state', 'in', ('not_paid', 'partial')),
             ('move_type', '=', 'out_invoice')])
        print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$',paid_invoices)
        for move in paid_invoices:
            if move.move_type == 'out_invoice':
                payment_ids = self.env['account.payment'].search([('partner_id', '=', move.partner_id.id), ('state', '=', 'posted')],order = 'date desc', limit=1)
                print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$',payment_ids,move.partner_id.name)
                if payment_ids.date:
                    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!', payment_ids.date)
                    print('************************************************************',date_now)
                    diff = date_now - payment_ids.date
                    print('###########################################', diff)
                    diff_days = diff.days
                    print('@@@@@@@@@@@@@@@@@@@@@@@', diff_days)
                    if payment_ids.paid == False and diff_days <= 31:
                        payment_ids.paid = True
                    if payment_ids.paid == False and diff_days > 31:
                        payment_ids.paid = True
                    if diff_days > 31 and payment_ids.paid == True :
                        template_id = self.env.ref('education_university_management.email_template_unpaid_student').id
                        template = self.env['mail.template'].browse(template_id)
                        print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&', template_id)
                        template.send_mail(move.id, force_send=True)



        # date_now = fields.Date.today()
        # print("@@@@@@@@@@@@@@@@@@@@@@@@@",date_now)
        # unpaid_invoices = self.search(
        #     [('state', '=', 'posted'), ('payment_state', 'in', ('not_paid', 'partial')), ('move_type', '=', 'out_invoice')])
        # print("#############################",unpaid_invoices)
        # for move in unpaid_invoices:
        #     if move.move_type == 'out_invoice':
        #         payment_ids = self.env['account.payment'].search(
        #             [('partner_id', '=', move.partner_id.id), ('state', '=', 'posted'),
        #              ('paid', '=', False)])
        #         if payment_ids:
        #             payment_ids.paid = True
        #             last_paid_date = payment_ids.
        #             default['date'] = date_utils.add(payment_ids.date, months=1)
        #         # print("#############################",payment_ids)
        #         if not payment_ids:
        #             template_id = self.env.ref('education_university_management.email_template_unpaid_student').id
        #             template = self.env['mail.template'].browse(template_id)
        #             print('*********************', template_id)
        #             template.send_mail(self.id, force_send=True)


# class InvoicePayment(models.Model):
#     _name = 'invoice.payment'
#
#     invoice_date = fields.Boolean('Paid')




