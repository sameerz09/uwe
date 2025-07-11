from odoo import models, api, fields
from dateutil.relativedelta import relativedelta


class SpendIncomeReport(models.Model):
    _name = 'x_spend.income.report'
    _description = 'Year-to-Date Spend and Income Report with 5% Tax in AED'

    @api.model
    def compute_and_send_yearly_report(self):
        today = fields.Date.today()
        year_start = today.replace(month=1, day=1)

        company_currency = self.env.company.currency_id  # Should be AED

        rows_html = ""
        current_month = year_start

        while current_month <= today:
            month_start = current_month
            month_end = (month_start + relativedelta(months=1)) - relativedelta(days=1)
            if month_end > today:
                month_end = today

            # ✅ Inbound payments: Customer
            customer_payments = self.env['account.payment'].search([
                ('payment_type', '=', 'inbound'),
                ('partner_type', '=', 'customer'),
                ('date', '>=', month_start),
                ('date', '<=', month_end),
                ('state', '=', 'posted')
            ])

            total_income = 0.0
            for payment in customer_payments:
                amount_aed = payment.currency_id._convert(
                    payment.amount,
                    company_currency,
                    payment.company_id,
                    payment.date or fields.Date.today()
                )
                total_income += amount_aed
            income_tax = total_income * 0.05

            # ✅ Outbound payments: Vendor
            vendor_payments = self.env['account.payment'].search([
                ('payment_type', '=', 'outbound'),
                ('partner_type', '=', 'supplier'),
                ('date', '>=', month_start),
                ('date', '<=', month_end),
                ('state', '=', 'posted')
            ])

            total_bills = 0.0
            for payment in vendor_payments:
                amount_aed = payment.currency_id._convert(
                    payment.amount,
                    company_currency,
                    payment.company_id,
                    payment.date or fields.Date.today()
                )
                total_bills += amount_aed
            bills_tax = total_bills * 0.05

            # ✅ Payroll: Assume always in AED
            payslips = self.env['hr.payslip'].search([
                ('state', '=', 'done'),
                ('date_from', '>=', month_start),
                ('date_to', '<=', month_end),
            ])
            total_payroll = sum(payslip.amount for payslip in payslips)

            # ✅ Calculate outcomes and net incomes
            total_outcome = total_bills + total_payroll
            net_income_without_tax = total_income - total_outcome
            net_income_with_tax = (total_income - income_tax) - (total_outcome + bills_tax)

            # ✅ Add row
            rows_html += f"""
                <tr>
                    <td>{month_start.strftime('%B %Y')}</td>
                    <td>{total_income:.2f} AED</td>
                    <td>{income_tax:.2f} AED</td>
                    <td>{total_bills:.2f} AED</td>
                    <td>{bills_tax:.2f} AED</td>
                    <td>{total_payroll:.2f} AED</td>
                    <td>{total_outcome:.2f} AED</td>
                    <td>{net_income_without_tax:.2f} AED</td>
                    <td>{net_income_with_tax:.2f} AED</td>
                </tr>
            """

            current_month += relativedelta(months=1)

        # ✅ Build final HTML email
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
                            max-width: 1200px;
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
                        <h2>Year-to-Date Spend and Income Report with 5% Tax in AED - {today.year}</h2>
                        <table>
                            <tr>
                                <th>Month</th>
                                <th>Total Income (AED)</th>
                                <th>5% Income Tax (AED)</th>
                                <th>Total Bills (AED)</th>
                                <th>5% Bills Tax (AED)</th>
                                <th>Total Payroll (AED)</th>
                                <th>Total Outcome (AED)</th>
                                <th>Net Income (No Tax) (AED)</th>
                                <th>Net Income (With Tax) (AED)</th>
                            </tr>
                            {rows_html}
                        </table>
                    </div>
                </body>
            </html>
        """

        self.env['mail.mail'].create({
            'subject': f"Year-to-Date Spend and Income Report with 5% Tax in AED - {today.year}",
            'body_html': html_content,
            'email_from': self.env.company.email or 'no-reply@example.com',
            'email_to': 'sameerzuheeri@gmail.com, sahel_alhabashneh@yahoo.com, Manager@uwuni.com',
        }).send()

        return True
