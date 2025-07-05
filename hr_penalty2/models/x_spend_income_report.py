from odoo import models, api, fields
from datetime import date
from dateutil.relativedelta import relativedelta

class SpendIncomeReport(models.Model):
    _name = 'x_spend.income.report'
    _description = 'Year-to-Date Spend and Income Report'

    @api.model
    def compute_and_send_yearly_report(self):
        today = fields.Date.today()
        year_start = today.replace(month=1, day=1)

        rows_html = ""
        current_month = year_start

        while current_month <= today:
            month_start = current_month
            month_end = (month_start + relativedelta(months=1)) - relativedelta(days=1)
            if month_end > today:
                month_end = today

            # Posted customer invoices
            invoices = self.env['account.move'].search([
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('invoice_date', '>=', month_start),
                ('invoice_date', '<=', month_end),
            ])
            total_income = sum(inv.amount_total for inv in invoices)

            # Posted vendor bills
            bills = self.env['account.move'].search([
                ('move_type', '=', 'in_invoice'),
                ('state', '=', 'posted'),
                ('invoice_date', '>=', month_start),
                ('invoice_date', '<=', month_end),
            ])
            total_bills = sum(bill.amount_total for bill in bills)

            # Done payslips
            payslips = self.env['hr.payslip'].search([
                ('state', '=', 'done'),
                ('date_from', '>=', month_start),
                ('date_to', '<=', month_end),
            ])
            total_payroll = sum(payslip.amount for payslip in payslips)

            total_outcome = total_bills + total_payroll
            net_income = total_income - total_outcome

            rows_html += f"""
                <tr>
                    <td>{month_start.strftime('%B %Y')}</td>
                    <td>{total_income:.2f}</td>
                    <td>{total_bills:.2f}</td>
                    <td>{total_payroll:.2f}</td>
                    <td>{total_outcome:.2f}</td>
                    <td>{net_income:.2f}</td>
                </tr>
            """

            current_month += relativedelta(months=1)

        # ✅ Build the final beautiful HTML
        html_content = f"""
            <html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            background-color: #f8f8f8;
                            padding: 20px;
                        }}
                        .report-container {{
                            max-width: 800px;
                            margin: auto;
                            background: #ffffff;
                            border-radius: 8px;
                            padding: 30px;
                            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                        }}
                        h2 {{
                            color: #333333;
                            text-align: center;
                        }}
                        table {{
                            width: 100%;
                            border-collapse: collapse;
                            margin-top: 20px;
                        }}
                        th, td {{
                            padding: 12px;
                            border-bottom: 1px solid #ddd;
                            text-align: left;
                        }}
                        th {{
                            background-color: #f2f2f2;
                        }}
                    </style>
                </head>
                <body>
                    <div class="report-container">
                        <h2>Year-to-Date Spend and Income Report - {today.year}</h2>
                        <table>
                            <tr>
                                <th>Month</th>
                                <th>Total Income</th>
                                <th>Total Bills</th>
                                <th>Total Payroll</th>
                                <th>Total Outcome</th>
                                <th>Net Income</th>
                            </tr>
                            {rows_html}
                        </table>
                    </div>
                </body>
            </html>
        """

        # ✅ Send the email, no attachment
        self.env['mail.mail'].create({
            'subject': f"Year-to-Date Spend and Income Report - {today.year}",
            'body_html': html_content,
            'email_from': self.env.company.email or 'no-reply@example.com',
            'email_to': 'sameerzuheeri@gmail.com',
        }).send()

        return True
