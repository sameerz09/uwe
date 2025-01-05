from odoo import fields, models, api, _


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_unpaid_invoice_reminder(self):
        unpaid_invoice_reminder = self.env["ir.config_parameter"].sudo().get_param("eg_unpaid_invoice_reminder.unpaid_invoice_reminder")
        if unpaid_invoice_reminder:
            invoice_ids = self.search([
                ("state", "=", "posted"),
                ("payment_state", "!=", "paid"),
                ("move_type", "in", ["out_invoice", "in_invoice"]),
                ("partner_id.unsubscribe_send_unpaid_invoice_mail", "=", False)
            ])
            for invoice_id in invoice_ids:
                mail_message = _("<p> Hello _person_name_, </p> <p>Your account ref _move_name_ total due amount _due_amount_ .</p><p>Thanks</p>")
                mail_message = mail_message.replace("_person_name_", invoice_id.partner_id.name or "")
                mail_message = mail_message.replace("_move_name_", invoice_id.name or "")
                mail_message = mail_message.replace("_due_amount_", str(invoice_id.amount_residual or 0))
                values = {
                    'model': invoice_id._name,
                    'res_id': invoice_id.id,
                    'subject': "Reminder for Unpaid Account No." + invoice_id.name,
                    'body': mail_message,
                    'body_html': mail_message,
                    'email_from': self.env.user.email,
                    'email_to': invoice_id.partner_id.email,
                }
                self.env['mail.mail'].create(values).send()
