from odoo import models, fields, api
from datetime import date, timedelta
import base64

class SpendIncomeReport(models.Model):
    _name = 'x_spend.income.report'
    _description = 'Monthly Spend and Income Report'

    @api.model
    def compute_and_send_monthly_report(self):
        today = fields.Date.today()
        month_start = today.replace(day=1)
        month_end = today

        # Income
        invoices = self.env['account.move'].search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('invoice_date', '>=', month_start),
            ('invoice_date', '<=', month_end),
        ])
        total_income = sum(inv.amount_total for inv in invoices)

        # Bills
        bills = self.env['account.move'].search([
            ('move_type', '=', 'in_invoice'),
            ('state', '=', 'posted'),
            ('invoice_date', '>=', month_start),
            ('invoice_date', '<=', month_end),
        ])
        total_bills = sum(bill.amount_total for bill in bills)

        # Payroll
        payslips = self.env['hr.payslip'].search([
            ('state', '=', 'done'),
            ('date_from', '>=', month_start),
            ('date_to', '<=', month_end),
        ])
        total_payroll = sum(p.amount for p in payslips)

        total_outcome = total_bills + total_payroll
        net_income = total_income - total_outcome

        # 🟢 Build HTML body
        body_html = f"""
            <h2>Spend / Income Report – {today.strftime('%B %Y')}</h2>
            <ul>
                <li><strong>Total Income:</strong> {total_income:.2f}</li>
                <li><strong>Total Bills:</strong> {total_bills:.2f}</li>
                <li><strong>Total Payroll:</strong> {total_payroll:.2f}</li>
                <li><strong>Total Outcome:</strong> {total_outcome:.2f}</li>
                <li><strong>Net Income:</strong> {net_income:.2f}</li>
            </ul>
        """

        # 🟢 Send the email — you can adjust recipients as needed
        self.env['mail.mail'].sudo().create({
            'subject': f'Spend & Income Report – {today.strftime("%B %Y")}',
            'body_html': body_html,
            'email_from': 'Finance Department <finance@yourcompany.com>',
            'email_to': 'manager@yourcompany.com',  # 👈 adjust this!
            'auto_delete': False,
        }).send()

        return True
