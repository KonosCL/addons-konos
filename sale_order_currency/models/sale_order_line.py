# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.tools.translate import _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    @api.multi
    def _prepare_invoice_line(self, qty):
        self.ensure_one()
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            company = self.env.user.company_id
            currency = self.order_id.pricelist_id.currency_id
            res.update({
                'price_unit': currency._convert(self.price_unit, company.currency_id, company, self.order_id.date_order or fields.Date.today()),
            })
        return res
