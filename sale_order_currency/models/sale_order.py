# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.tools.translate import _


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    convert_to_company_currency = fields.Boolean(u'Convertir a moneda local?')

    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        if self.convert_to_company_currency:
            invoice_vals.update({
                'currency_id': self.company_id.currency_id.id,
            })
        return invoice_vals
