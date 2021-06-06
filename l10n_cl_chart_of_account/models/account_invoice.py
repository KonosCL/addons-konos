# -*- coding: utf-8 -*-
from odoo import api, models, fields, _


class AccountInvoiceTax(models.Model):
    _inherit = "account.invoice.tax"

    amount_retencion = fields.Monetary(
            string="Retención",
            default=0.00,
        )
    retencion_account_id = fields.Many2one(
            'account.account',
            string='Tax Account',
            domain=[('deprecated', '=', False)],
        )

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
        'invoice_id.date_invoice', 'invoice_id.date')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id, uom_id=self.uom_id)
        self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
        self.price_total = taxes['total_included'] if taxes else self.price_subtotal
        if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id._get_currency_rate_date()).compute(price_subtotal_signed, self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign



class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    amount_retencion = fields.Monetary(
        string="Retención",
        default=0.00,
        compute='_compute_amount',
    )

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice', 'type')
    def _compute_amount(self):
        #@TODO Buscar una mejor forma de aplicar retención
        amount_retencion = 0
        neto = 0
        amount_tax = 0
        included = False
        for tax in self.tax_line_ids:
            if tax.tax_id.price_include:
                included = True
            amount_tax += tax.amount
            amount_retencion += tax.amount_retencion
        self.amount_retencion = amount_retencion
        neto += sum((line.price_subtotal.with_context(round=False).compute_all(
            line.price_unit,self.currency_id, line.quantity,
            line.product_id, self.partner_id, discount=line.discount
            )['total_excluded']) for line in self.invoice_line_ids)
        self.amount_untaxed = neto
        self.amount_tax = amount_tax
        self.amount_total = neto + amount_tax - amount_retencion
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = self.currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign


    @api.multi
    def get_taxes_values(self):
        tax_grouped = {}
        round_curr = self.currency_id.round
        for line in self.invoice_line_ids:
            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity, line.product_id, self.partner_id, uom_id=line.uom_id)['taxes']
            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
                key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)

                if key not in tax_grouped:
                    tax_grouped[key] = val
                    tax_grouped[key]['base'] = round_curr(val['base'])
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += round_curr(val['base'])
        return tax_grouped
