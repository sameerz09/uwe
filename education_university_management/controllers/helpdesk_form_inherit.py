from odoo import http
from odoo.http import request
import logging
from odoo.addons.website.controllers.form import WebsiteForm
_logger = logging.getLogger(__name__)


class CustomWebsiteHelpdesk(http.Controller):
    @http.route(['/website/form/helpdesk.ticket'], type='http', auth="public", website=True, csrf=False)
    def website_form_ticket(self, **kwargs):
        try:
            # Get and sanitize the team_id value
            team_id_raw = kwargs.get('team_id', '0')  # Default to '0' if not provided
            team_id = int(team_id_raw.split(',')[0].strip())  # Extract the first valid number
        except ValueError:
            # Log the error and fallback to a default or no team_id
            _logger.error(f"Invalid team_id value: {kwargs.get('team_id')}")
            team_id = False

        # Create the helpdesk ticket
        request.env['helpdesk.ticket'].sudo().create({
            'name': kwargs.get('name'),
            'description': kwargs.get('description'),
            'partner_id': request.env.user.partner_id.id,
            'team_id': team_id,  # Use sanitized team_id
        })

        # Redirect to a success page
        return request.redirect('/your-ticket-has-been-submitted')

class WebsiteFormInherit(WebsiteForm):
    def _handle_website_form(self, model_name, **kwargs):
        # Handle team_id parsing and validation
        team_id_raw = kwargs.get('team_id', '0')
        try:
            # Clean and convert team_id
            team_id = int(team_id_raw.split(',')[0].strip())
            kwargs['team_id'] = team_id
        except ValueError:
            # If parsing fails, log the error and fallback
            kwargs['team_id'] = False
            request.env['ir.logging'].sudo().create({
                'name': 'Helpdesk Form Error',
                'type': 'server',
                'dbname': request.env.cr.dbname,
                'message': f"Invalid team_id value: {team_id_raw}",
                'level': 'error',
            })

        # Call the original method
        return super(WebsiteFormInherit, self)._handle_website_form(model_name, **kwargs)
