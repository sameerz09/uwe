# -*- coding: utf-8 -*-
# from odoo import http


# class UwePayroll(http.Controller):
#     @http.route('/uwe_payroll/uwe_payroll', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/uwe_payroll/uwe_payroll/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('uwe_payroll.listing', {
#             'root': '/uwe_payroll/uwe_payroll',
#             'objects': http.request.env['uwe_payroll.uwe_payroll'].search([]),
#         })

#     @http.route('/uwe_payroll/uwe_payroll/objects/<model("uwe_payroll.uwe_payroll"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('uwe_payroll.object', {
#             'object': obj
#         })

