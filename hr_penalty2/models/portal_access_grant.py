from odoo import models, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def cron_auto_grant_portal_access(self):
        """Automatically grant portal access to partners without user accounts."""
        PortalWizard = self.env['portal.wizard']
        PortalWizardUser = self.env['portal.wizard.user']

        partners = self.env['res.partner'].search([
            ('email', '!=', False),
            ('user_ids', '=', False)
        ])

        if partners:
            wizard = PortalWizard.create({})
            for partner in partners:
                wizard_user = PortalWizardUser.create({
                    'wizard_id': wizard.id,
                    'partner_id': partner.id,
                    'email': partner.email
                })
                # ✅ Call the grant access on each wizard user
                wizard_user.action_grant_access()
