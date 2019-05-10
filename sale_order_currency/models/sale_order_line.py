# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.tools.translate import _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    @api.multi
    def _prepare_invoice_line(self, qty):
        self.ensure_one()
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        price_unit = self.price_unit
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.order_id.date_order)
            price_unit = currency_id.compute(price_unit, self.company_id.currency_id)
        res.update({
            'price_unit': price_unit,
        })
        return res
