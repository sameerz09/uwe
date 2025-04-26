from odoo import models, fields, api, _
from datetime import date, timedelta
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    last_reminder_date = fields.Date(string="Last Reminder Date")  # Track the last sent date

    def action_unpaid_invoice_reminder(self):
        _logger.info("📧 Starting daily unpaid invoice reminder process...")

        # Check if reminder feature is enabled
        config_key = "eg_unpaid_invoice_reminder.unpaid_invoice_reminder"
        reminder_enabled = self.env["ir.config_parameter"].sudo().get_param(config_key)
        if reminder_enabled != "True":
            _logger.warning("⚠️ Invoice reminder is disabled in settings. Exiting.")
            return

        today = date.today()
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        total_sent = 0

        # Search only for invoices that are overdue and not reminded today
        invoices = self.search([
            ("state", "=", "posted"),
            ("payment_state", "!=", "paid"),
            ("move_type", "=", "out_invoice"),
            ("partner_id.unsubscribe_send_unpaid_invoice_mail", "=", False),
            "|",  # Either last_reminder_date is not today OR it's null
            ("last_reminder_date", "!=", today),
            ("last_reminder_date", "=", False),
        ])

        pre_due_notice_date = today + timedelta(days=7)
        _logger.info("🔍 Found %s invoices needing reminders.", len(invoices))

        for invoice in invoices:
            partner = invoice.partner_id

            if not partner.email:
                _logger.warning("❌ Skipping %s: Partner %s has no email.", invoice.name, partner.name)
                continue

            access_token = invoice._portal_ensure_token()
            invoice_url = f"{base_url}/my/invoices/{invoice.id}?access_token={access_token}"

            if invoice.invoice_date_due == pre_due_notice_date:
                subject = f"Upcoming Invoice Notification – {invoice.name}"
                body_html = _(
                    "<p>Hello <strong>{name}</strong>,</p>"
                    "<p>This is a friendly reminder that your invoice <strong>{ref}</strong> "
                    "is due in 7 days with an amount of <strong>{amount}</strong>.</p>"
                    "<p>You can view it below:</p>"
                    "<p><a href='{url}' style='background:#2196F3;color:white;padding:10px 20px;"
                    "text-decoration:none;border-radius:5px;'>View Invoice</a></p>"
                    "<p>Best regards,<br/>Finance Department</p>"
                ).format(
                    name=partner.name or "",
                    ref=invoice.name or "",
                    amount=invoice.amount_residual,
                    url=invoice_url,
                )
            elif invoice.invoice_date_due < today:
                subject = f"Overdue Invoice Reminder – {invoice.name}"
                body_html = _(
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
                    url=invoice_url,
                )
            else:
                _logger.info("ℹ️ Skipping invoice %s: Not due soon or overdue.", invoice.name)
                continue

            try:
                self.env["mail.mail"].sudo().create({
                    "model": invoice._name,
                    "res_id": invoice.id,
                    "subject": subject,
                    "body_html": body_html,
                    "email_to": partner.email,
                    "email_from": "Finance Department <notifications@uwuni.com>",
                    "auto_delete": False,
                }).send()

                # Update the last reminder date
                invoice.sudo().write({'last_reminder_date': today})
                total_sent += 1
                _logger.info("✅ Sent reminder for invoice %s to %s", invoice.name, partner.email)

            except Exception as e:
                _logger.exception("❌ Failed to send reminder for invoice %s: %s", invoice.name, str(e))

        _logger.info("📬 Total reminders sent today: %s", total_sent)
