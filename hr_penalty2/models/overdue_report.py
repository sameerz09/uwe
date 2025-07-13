from odoo import models, api, fields
from datetime import timedelta

class OverdueDebtsBillsReport(models.Model):
    _name = 'overdue.debts.bills.report'
    _description = 'Overdue Debts Report (Customer Invoices Only)'

    @api.model
    def compute_and_send_overdue_report(self):
        today = fields.Date.today()

        overdue_invoices = self.env['account.move'].search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('invoice_date_due', '<', today),
            ('amount_residual', '>', 0),
        ])

        total_count = len(overdue_invoices)
        total_amount = sum(inv.amount_residual for inv in overdue_invoices)

        # Calculate age buckets
        one_month = today - timedelta(days=30)
        three_months = today - timedelta(days=90)
        six_months = today - timedelta(days=180)
        one_year = today - timedelta(days=365)

        over_1m = sum(inv.amount_residual for inv in overdue_invoices if inv.invoice_date_due <= one_month)
        over_3m = sum(inv.amount_residual for inv in overdue_invoices if inv.invoice_date_due <= three_months)
        over_6m = sum(inv.amount_residual for inv in overdue_invoices if inv.invoice_date_due <= six_months)
        over_1y = sum(inv.amount_residual for inv in overdue_invoices if inv.invoice_date_due <= one_year)

        # Build rows
        rows_html = ""
        for inv in overdue_invoices:
            rows_html += f"""
                <tr>
                    <td>{inv.name}</td>
                    <td>{inv.partner_id.name or ''}</td>
                    <td>{inv.invoice_date_due or ''}</td>
                    <td>{inv.amount_residual:.2f}</td>
                </tr>
            """

        if not rows_html:
            rows_html = "<tr><td colspan='4' style='text-align:center;'>✅ No overdue customer invoices!</td></tr>"

        # Full HTML with dashboard
        html_content = f"""
            <html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            background-color: #f9f9f9;
                            padding: 20px;
                        }}
                        .report-container {{
                            max-width: 900px;
                            margin: auto;
                            background: #ffffff;
                            border-radius: 8px;
                            padding: 30px;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                        }}
                        h2 {{
                            color: #333333;
                            text-align: center;
                        }}
                        .dashboard {{
                            display: flex;
                            flex-wrap: wrap;
                            justify-content: space-between;
                            margin-bottom: 30px;
                        }}
                        .card {{
                            flex: 1 0 45%;
                            background: #f2f2f2;
                            border-radius: 5px;
                            margin: 10px;
                            padding: 20px;
                            text-align: center;
                        }}
                        .card h3 {{
                            margin: 0;
                            font-size: 18px;
                            color: #555;
                        }}
                        .card p {{
                            font-size: 24px;
                            margin: 5px 0 0;
                            font-weight: bold;
                            color: #000;
                        }}
                        table {{
                            width: 100%;
                            border-collapse: collapse;
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
                        <h2>Overdue Customer Invoices Report - {today.strftime('%B %Y')}</h2>
                        <div class="dashboard">
                            <div class="card">
                                <h3>Total Overdue Invoices</h3>
                                <p>{total_count}</p>
                            </div>
                            <div class="card">
                                <h3>Total Overdue Amount</h3>
                                <p>{total_amount:.2f}</p>
                            </div>
                            <div class="card">
                                <h3>> 1 Month</h3>
                                <p>{over_1m:.2f}</p>
                            </div>
                            <div class="card">
                                <h3>> 3 Months</h3>
                                <p>{over_3m:.2f}</p>
                            </div>
                            <div class="card">
                                <h3>> 6 Months</h3>
                                <p>{over_6m:.2f}</p>
                            </div>
                            <div class="card">
                                <h3>> 1 Year</h3>
                                <p>{over_1y:.2f}</p>
                            </div>
                        </div>
                        <table>
                            <tr>
                                <th>Document</th>
                                <th>Customer</th>
                                <th>Due Date</th>
                                <th>Residual Amount</th>
                            </tr>
                            {rows_html}
                        </table>
                    </div>
                </body>
            </html>
        """

        self.env['mail.mail'].create({
            'subject': f"Overdue Customer Invoices Report - {today.strftime('%B %Y')}",
            'body_html': html_content,
            'email_from': self.env.company.email or 'no-reply@example.com',
            'email_to': 'sameerzuheeri@gmail.com, sahel_alhabashneh@yahoo.com, Manager@uwuni.com, Account@uwuni.com',
        }).send()

        return True
