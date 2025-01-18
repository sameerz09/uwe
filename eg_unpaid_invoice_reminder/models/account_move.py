from odoo import fields, models, api, _
from datetime import date

class AccountMove(models.Model):
    _inherit = "account.move"

    def action_unpaid_invoice_reminder(self):
        unpaid_invoice_reminder = self.env["ir.config_parameter"].sudo().get_param(
            "eg_unpaid_invoice_reminder.unpaid_invoice_reminder"
        )
        if unpaid_invoice_reminder:
            # Get the server's domain
            server_domain = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
            today = date.today()
            invoice_ids = self.search([
                ("state", "=", "posted"),
                ("payment_state", "!=", "paid"),
                ("move_type", "in", ["out_invoice"]),
                ("partner_id.unsubscribe_send_unpaid_invoice_mail", "=", False),
                ("invoice_date_due", "<=", today),
            ])
            for invoice_id in invoice_ids:
                access_token = invoice_id._portal_ensure_token()
                # Construct the full URL with the domain
                preview_url = f"{server_domain}/my/invoices/{invoice_id.id}?access_token={access_token}"

                mail_message = _(
                    "<p>Hello <strong>_person_name_</strong>,</p>"
                    "<p>Your account ref <strong>_move_name_</strong> has a total due amount of "
                    "<strong>_due_amount_</strong>.</p>"
                    "<p>You can preview your invoice by clicking the button below:</p>"
                    "<p><a href='_preview_url_' style='background-color: #4CAF50; color: white; "
                    "padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; "
                    "border-radius: 5px;'>View Invoice</a></p>"
                    "<p>Thanks,</p>"
                )
                mail_message = mail_message.replace("_person_name_", invoice_id.partner_id.name or "")
                mail_message = mail_message.replace("_move_name_", invoice_id.name or "")
                mail_message = mail_message.replace("_due_amount_", str(invoice_id.amount_residual or 0))
                mail_message = mail_message.replace("_preview_url_", preview_url)

                values = {
                    'model': invoice_id._name,
                    'res_id': invoice_id.id,
                    'subject': f"Reminder for Unpaid Account No. {invoice_id.name}",
                    'body': mail_message,
                    'body_html': mail_message,
                    'email_to': invoice_id.partner_id.email,
                }
                self.env['mail.mail'].sudo().create(values).send()

