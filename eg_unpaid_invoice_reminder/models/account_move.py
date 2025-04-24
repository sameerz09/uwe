from odoo import models, fields, api, _
from datetime import date, timedelta
import logging
import time

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    def action_unpaid_invoice_reminder(self):
        _logger.info("📧 Starting invoice reminder process...")

        config_key = "eg_unpaid_invoice_reminder.unpaid_invoice_reminder"
        reminder_enabled = self.env["ir.config_parameter"].sudo().get_param(config_key)
        if reminder_enabled != "True":
            _logger.warning("⚠️ Reminder is disabled. Skipping.")
            return

        today = date.today()
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        batch_size = 5
        total_sent = 0

        invoices = self.search([
            ("state", "=", "posted"),
            ("payment_state", "!=", "paid"),
            ("move_type", "=", "out_invoice"),
            ("partner_id.unsubscribe_send_unpaid_invoice_mail", "=", False),
        ])

        pre_due_notice_date = today + timedelta(days=7)
        _logger.info("📆 Today: %s | Preparing pre-due notices for due date: %s", today, pre_due_notice_date)

        for i in range(0, len(invoices), batch_size):
            batch = invoices[i:i + batch_size]
            for invoice in batch:
                partner = invoice.partner_id
                if not partner.email:
                    _logger.warning("❌ Skipping invoice %s: Missing email for %s", invoice.name, partner.name)
                    continue

                access_token = invoice._portal_ensure_token()
                invoice_url = f"{base_url}/my/invoices/{invoice.id}?access_token={access_token}"

                try:
                    if invoice.invoice_date_due == pre_due_notice_date:
                        subject = f"Upcoming Invoice Notification – {invoice.name}"
                        body = _(
                            "<p>Hello <strong>{name}</strong>,</p>"
                            "<p>This is a gentle reminder that your invoice <strong>{ref}</strong> "
                            "is due in 7 days with an amount of <strong>{amount}</strong>.</p>"
                            "<p>You can preview it below:</p>"
                            "<p><a href='{url}' style='background:#2196F3;color:white;padding:10px 20px;"
                            "text-decoration:none;border-radius:5px;'>Preview Invoice</a></p>"
                            "<p>Best regards,<br/>Finance Department</p>"
                        ).format(
                            name=partner.name or "",
                            ref=invoice.name or "",
                            amount=invoice.amount_residual,
                            url=invoice_url
                        )
                    elif invoice.invoice_date_due < today:
                        subject = f"Overdue Invoice Reminder – {invoice.name}"
                        body = _(
                            "<p>Hello <strong>{name}</strong>,</p>"
                            "<p>This is a daily reminder that your invoice <strong>{ref}</strong> "
                            "is overdue with an amount of <strong>{amount}</strong>.</p>"
                            "<p>Please take action to avoid penalties:</p>"
                            "<p><a href='{url}' style='background:#F44336;color:white;padding:10px 20px;"
                            "text-decoration:none;border-radius:5px;'>Pay Invoice</a></p>"
                            "<p>Best regards,<br/>Finance Department</p>"
                        ).format(
                            name=partner.name or "",
                            ref=invoice.name or "",
                            amount=invoice.amount_residual,
                            url=invoice_url
                        )
                    else:
                        continue

                    mail = self.env["mail.mail"].sudo().create({
                        "model": invoice._name,
                        "res_id": invoice.id,
                        "subject": subject,
                        "body_html": body,
                        "email_to": partner.email,
                        "email_from": "Finance Department <notifications@uwuni.com>",
                        "state": "outgoing",  # Ensures retry if fails
                    })

                    mail.send()
                    total_sent += 1
                    _logger.info("✅ Sent '%s' to %s", subject, partner.email)

                except Exception as e:
                    _logger.exception("❌ Failed to queue/send for invoice %s: %s", invoice.name, str(e))

            time.sleep(2)

        _logger.info("📬 Total emails queued or sent: %d", total_sent)
