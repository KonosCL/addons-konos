# -*- coding: utf-8 -*-
from openerp import http

# class PayrollCancel(http.Controller):
#     @http.route('/payroll_cancel/payroll_cancel/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/payroll_cancel/payroll_cancel/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('payroll_cancel.listing', {
#             'root': '/payroll_cancel/payroll_cancel',
#             'objects': http.request.env['payroll_cancel.payroll_cancel'].search([]),
#         })

#     @http.route('/payroll_cancel/payroll_cancel/objects/<model("payroll_cancel.payroll_cancel"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('payroll_cancel.object', {
#             'object': obj
#         })