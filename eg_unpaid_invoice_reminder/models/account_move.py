from odoo import models, fields, api, _
from datetime import date
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    def action_unpaid_invoice_reminder(self):
        _logger.info("📧 Initiating unpaid invoice reminder process.")

        config_key = "eg_unpaid_invoice_reminder.unpaid_invoice_reminder"
        reminder_enabled = self.env["ir.config_parameter"].sudo().get_param(config_key)
        _logger.info("🔧 Config [%s] = %s", config_key, reminder_enabled)

        if reminder_enabled != "True":
            _logger.warning("⚠️ Unpaid invoice reminder is disabled. Skipping operation.")
            return

        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        today = date.today()
        _logger.info("📅 Processing invoices due on or before: %s", today)

        invoices = self.search([
            ("state", "=", "posted"),
            ("payment_state", "!=", "paid"),
            ("move_type", "=", "out_invoice"),
            ("partner_id.unsubscribe_send_unpaid_invoice_mail", "=", False),
            ("invoice_date_due", "<=", today),
        ])

        _logger.info("🔍 Found %s unpaid invoice(s) for reminder.", len(invoices))

        for invoice in invoices:
            partner = invoice.partner_id
            if not partner.email:
                _logger.warning("❌ Skipping invoice %s: Missing email for partner %s", invoice.name, partner.name)
                continue

            try:
                access_token = invoice._portal_ensure_token()
                invoice_url = f"{base_url}/my/invoices/{invoice.id}?access_token={access_token}"
                _logger.debug("🔗 Generated portal link: %s", invoice_url)

                body = _(
                    "<p>Hello <strong>{name}</strong>,</p>"
                    "<p>Your account reference <strong>{ref}</strong> has an outstanding amount of "
                    "<strong>{amount}</strong>.</p>"
                    "<p>You can review your invoice by clicking the button below:</p>"
                    "<p><a href='{url}' style='background-color: #4CAF50; color: white; "
                    "padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; "
                    "border-radius: 5px;'>View Invoice</a></p>"
                    "<p>Best regards,<br/>Finance Department</p>"
                ).format(
                    name=partner.name or "",
                    ref=invoice.name or "",
                    amount=invoice.amount_residual or "0.0",
                    url=invoice_url
                )

                mail_values = {
                    "model": invoice._name,
                    "res_id": invoice.id,
                    "subject": f"Reminder for Unpaid Account No. {invoice.name}",
                    "body": body,
                    "body_html": body,
                    "email_to": partner.email,
                    "email_from": "Finance Department <notifications@uwuni.com>",
                }

                mail = self.env["mail.mail"].sudo().create(mail_values)
                mail.send()
                _logger.info("✅ Email sent for invoice %s to %s", invoice.name, partner.email)

            except Exception as e:
                _logger.exception("❌ Failed to send reminder for invoice %s: %s", invoice.name, str(e))
