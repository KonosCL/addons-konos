# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.tools.translate import _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'currency_id': self.company_id.currency_id.id,
        })
        return invoice_vals
