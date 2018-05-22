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
                    price_tax_included += line.price_tax_included
            if price_tax_included > 0 and  tax.tax_id.sii_type in ["R"] and tax.tax_id.amount > 0:
                base = currency.round(price_tax_included)
            elif price_tax_included > 0 and tax.tax_id.amount > 0:
                base = currency.round(price_tax_included / ( 1 + tax.tax_id.amount / 100.0))
            neto += base
        return neto


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _compute_amount(self):
        #@TODO Buscar una mejor forma de aplicar retención
        for inv in self:
            amount_retencion = 0
            neto = 0
            amount_tax = 0
            included = False
            for tax in inv.tax_line_ids:
                if tax.tax_id.price_include:
                    included = True
                amount_tax += tax.amount
                amount_retencion  += tax.amount_retencion
            inv.amount_retencion = amount_retencion
            if included:
                neto += inv.tax_line_ids._getNeto(inv.currency_id)
                amount_retencion += amount_retencion
            else:
                neto += sum(line.price_subtotal for line in inv.invoice_line_ids)
            inv.amount_untaxed = neto
            inv.amount_tax = amount_tax
            inv.amount_total = inv.amount_untaxed + inv.amount_tax - amount_retencion
            amount_total_company_signed = inv.amount_total
            amount_untaxed_signed = inv.amount_untaxed
            if inv.currency_id and inv.currency_id != inv.company_id.currency_id:
                currency_id = inv.currency_id.with_context(date=inv.date_invoice)
                amount_total_company_signed = currency_id.compute(inv.amount_total, inv.company_id.currency_id)
                amount_untaxed_signed = inv.currency_id.compute(inv.amount_untaxed, inv.company_id.currency_id)
            sign = inv.type in ['in_refund', 'out_refund'] and -1 or 1
            inv.amount_total_company_signed = amount_total_company_signed * sign
            inv.amount_total_signed = inv.amount_total * sign
            inv.amount_untaxed_signed = amount_untaxed_signed * sign

    amount_retencion = fields.Monetary(
        string="Retención",
        default=0.00,
        compute='_compute_amount',
    )
