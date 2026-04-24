# -*- coding: utf-8 -*-
import base64
import logging
from odoo import http, fields
from odoo.http import request

_logger = logging.getLogger(__name__)


class UweSignController(http.Controller):

    @http.route(['/my/sign', '/my/sign/list'], type='http', auth='user', website=True)
    def sign_list(self, **kw):
        env = request.env
        employee = env['hr.employee'].sudo().search(
            [('user_id', '=', env.user.id)], limit=1
        )
        domain = [('state', 'in', ['waiting', 'signed', 'refused'])]
        if employee:
            domain.append(('employee_id', '=', employee.id))
        else:
            domain.append(('partner_id', '=', env.user.partner_id.id))

        documents = env['uwe.sign.document'].sudo().search(domain)
        return request.render('uwe_sign.portal_sign_list', {
            'documents': documents,
            'page_name': 'sign_list',
        })

    @http.route(['/my/sign/<int:doc_id>'], type='http', auth='user', website=True)
    def sign_document(self, doc_id, **kw):
        document = request.env['uwe.sign.document'].sudo().browse(doc_id)
        if not document.exists():
            return request.redirect('/my/sign')

        user_name = request.env.user.name or ''
        return request.render('uwe_sign.portal_sign_document', {
            'document': document,
            'user_name': user_name,
            'page_name': 'sign_document',
            'success': kw.get('success'),
        })

    @http.route(['/my/sign/<int:doc_id>/submit'], type='json', auth='user', website=True, methods=['POST'])
    def sign_submit(self, doc_id, signature=None, **kw):
        document = request.env['uwe.sign.document'].sudo().browse(doc_id)
        if not document.exists():
            return {'success': False, 'error': 'Document not found.'}
        if document.state != 'waiting':
            return {'success': False, 'error': 'Document is not pending signature.'}
        if not signature:
            return {'success': False, 'error': 'No signature provided.'}

        try:
            sig_data = signature
            if ',' in sig_data:
                sig_data = sig_data.split(',', 1)[1]
            document.write({
                'signature': sig_data,
                'signed_by': request.env.user.name,
                'signed_date': fields.Datetime.now(),
                'state': 'signed',
            })
            document.message_post(body=f"Document signed by {request.env.user.name}.")
            return {'success': True}
        except Exception as e:
            _logger.error("Sign submit error: %s", e)
            return {'success': False, 'error': str(e)}
