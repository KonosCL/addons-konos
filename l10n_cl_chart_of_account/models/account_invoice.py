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

    def _getNeto(self, currency):
        neto = 0
        for tax in self:
            base = tax.base
            price_tax_included = 0
            #amount_tax +=tax.amount
            for line in tax.invoice_id.invoice_line_ids:
                if tax.tax_id in line.invoice_line_tax_ids and tax.tax_id.price_include:
                    price_tax_included += line.price_total
            if price_tax_included > 0 and tax.tax_id.sii_type in ["R"] and tax.tax_id.amount > 0:
                base = currency.round(price_tax_included)
            elif price_tax_included > 0 and tax.tax_id.amount > 0:
                base = currency.round(price_tax_included / ( 1 + tax.tax_id.amount / 100.0))
            neto += base
        return neto


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

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
        if included:
            neto += self.tax_line_ids._getNeto(self.currency_id)
            amount_retencion += amount_retencion
        else:
            neto += sum(line.price_subtotal for line in self.invoice_line_ids)
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

    amount_retencion = fields.Monetary(
        string="Retención",
        default=0.00,
        compute='_compute_amount',
    )
