# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
import math


class AccountTaxTemplate(models.Model):
    _inherit = 'account.tax.template'

    sii_code = fields.Integer(
            string='SII Code',
        )
    sii_type = fields.Selection(
            [
                    ('A','Anticipado'),
                    ('R','Retención'),
            ],
            string="Tipo de impuesto para el SII",
        )
    retencion = fields.Float(
            string="Valor retención",
            default=0.00,
        )
    no_rec = fields.Boolean(
            string="Es No Recuperable",
            default=False,
        )
    activo_fijo = fields.Boolean(
            string="Activo Fijo",
            default=False,
        )
    sii_detailed = fields.Boolean(
            string='Desglose de IVA',
            default=False,
        )
    uom_id = fields.Many2one(
        'uom.uom',
        string="Force Uom"
    )
    mepco = fields.Selection(
        [
            ('diesel', 'Diesel'),
            ('gasolina_93', 'Gasolina 93'),
            ('gasolina_97', 'Gasolina 97'),
        ],
        string="Indicador Mepco",
    )

    def _get_tax_vals(self, company, tax_template_to_tax):
        """ This method generates a dictionnary of all the values for the tax that will be created.
        """
        self.ensure_one()
        val = super(AccountTaxTemplate, self)._get_tax_vals(company, tax_template_to_tax)
        val.update({
            'sii_code': self.sii_code,
            'sii_type': self.sii_type,
            'retencion': self.retencion,
            'no_rec': self.no_rec,
            'activo_fijo': self.activo_fijo,
            'sii_detailed': self.sii_detailed,
            'uom_id': self.uom_id.id,
            'mepco': self.mepco,
        })
        return val


class AccountTax(models.Model):
    _inherit = 'account.tax'

    sii_code = fields.Integer(
            string='SII Code',
        )
    sii_type = fields.Selection(
            [
                    ('A','Anticipado'),
                    ('R','Retención'),
            ],
            string="Tipo de impuesto para el SII",
        )
    retencion = fields.Float(
            string="Valor retención",
            default=0.00,
        )
    no_rec = fields.Boolean(
            string="Es No Recuperable",
            default=False,
        )
    activo_fijo = fields.Boolean(
            string="Activo Fijo",
            default=False,
        )
    sii_detailed = fields.Boolean(
            string='Desglose de IVA',
            default=False,
        )
    uom_id = fields.Many2one(
        'uom.uom',
        string="Force Uom"
    )
    mepco = fields.Selection(
        [
            ('diesel', 'Diesel'),
            ('gasolina_93', 'Gasolina 93'),
            ('gasolina_97', 'Gasolina 97'),
        ],
        string="Indicador Mepco",
    )

    def compute_factor(self, uom_id):
        amount_tax = self.amount or 0.0
        if self.uom_id and self.uom_id != uom_id:
            factor = self.uom_id._compute_quantity(1, uom_id)
            amount_tax = (amount_tax / factor)
        return amount_tax

    def _compute_amount(self, base_amount, price_unit, quantity=1.0, product=None, partner=None, uom_id=None):
        """ Returns the amount of a single tax. base_amount is the actual amount on which the tax is applied, which is
            price_unit * quantity eventually affected by previous taxes (if tax is include_base_amount XOR price_include)
        """
        self.ensure_one()
        if self.amount_type == 'fixed':
            # Use copysign to take into account the sign of the base amount which includes the sign
            # of the quantity and the sign of the price_unit
            # Amount is the fixed price for the tax, it can be negative
            # Base amount included the sign of the quantity and the sign of the unit price and when
            # a product is returned, it can be done either by changing the sign of quantity or by changing the
            # sign of the price unit.
            # When the price unit is equal to 0, the sign of the quantity is absorbed in base_amount then
            # a "else" case is needed
            amount_tax = self.compute_factor(uom_id)
            if base_amount:
                return math.copysign(quantity, base_amount) * amount_tax
            else:
                return quantity * amount_tax
        price_include = self.price_include or self._context.get('force_price_include')

        if (self.amount_type == 'percent' and not price_include) or (self.amount_type == 'division' and price_include):
            return base_amount * self.amount / 100
        if self.amount_type == 'percent' and price_include:
            return base_amount - (base_amount / (1 + self.amount / 100))
        if self.amount_type == 'division' and not price_include:
            return base_amount / (1 - self.amount / 100) - base_amount


    @api.multi
    def compute_all(self, price_unit, currency=None, quantity=1.0, product=None, partner=None, uom_id=None):
        """ Returns all information required to apply taxes (in self + their children in case of a tax goup).
            We consider the sequence of the parent for group of taxes.
                Eg. considering letters as taxes and alphabetic order as sequence :
                [G, B([A, D, F]), E, C] will be computed as [A, D, F, C, E, G]

        RETURN: {
            'total_excluded': 0.0,    # Total without taxes
            'total_included': 0.0,    # Total with taxes
            'taxes': [{               # One dict for each tax in self and their children
                'id': int,
                'name': str,
                'amount': float,
                'sequence': int,
                'account_id': int,
                'refund_account_id': int,
                'analytic': boolean,
            }]
        } """
        if len(self) == 0:
            company_id = self.env.user.company_id
        else:
            company_id = self[0].company_id
        if not currency:
            currency = company_id.currency_id
        taxes = []
        # By default, for each tax, tax amount will first be computed
        # and rounded at the 'Account' decimal precision for each
        # PO/SO/invoice line and then these rounded amounts will be
        # summed, leading to the total amount for that tax. But, if the
        # company has tax_calculation_rounding_method = round_globally,
        # we still follow the same method, but we use a much larger
        # precision when we round the tax amount for each line (we use
        # the 'Account' decimal precision + 5), and that way it's like
        # rounding after the sum of the tax amounts of each line
        prec = currency.decimal_places

        # In some cases, it is necessary to force/prevent the rounding of the tax and the total
        # amounts. For example, in SO/PO line, we don't want to round the price unit at the
        # precision of the currency.
        # The context key 'round' allows to force the standard behavior.
        round_tax = False if company_id.tax_calculation_rounding_method == 'round_globally' else True
        round_total = True
        if 'round' in self.env.context:
            round_tax = bool(self.env.context['round'])
            round_total = bool(self.env.context['round'])

        if not round_tax:
            prec += 5

        base_values = self.env.context.get('base_values')
        if not base_values:
            total_excluded = total_included = base = round(price_unit * quantity, prec)
        else:
            total_excluded, total_included, base = base_values

        # Sorting key is mandatory in this case. When no key is provided, sorted() will perform a
        # search. However, the search method is overridden in account.tax in order to add a domain
        # depending on the context. This domain might filter out some taxes from self, e.g. in the
        # case of group taxes.
        for tax in self.sorted(key=lambda r: r.sequence):
            # Allow forcing price_include/include_base_amount through the context for the reconciliation widget.
            # See task 24014.
            price_include = self._context.get('force_price_include', tax.price_include)
            if tax.amount_type == 'group':
                children = tax.children_tax_ids.with_context(base_values=(total_excluded, total_included, base))
                ret = children.compute_all(price_unit, currency, quantity, product, partner, uom_id)
                total_excluded = ret['total_excluded']
                base = ret['base'] if tax.include_base_amount else base
                total_included = ret['total_included']
                tax_amount = total_included - total_excluded
                taxes += ret['taxes']
                continue

            tax_amount = tax._compute_amount(base, price_unit, quantity, product, partner, uom_id)
            if not round_tax:
                tax_amount = round(tax_amount, prec)
            else:
                tax_amount = currency.round(tax_amount)

            if price_include:
                total_excluded -= tax_amount
                base -= tax_amount
            else:
                total_included += tax_amount

            # Keep base amount used for the current tax
            tax_base = base

            if tax.include_base_amount:
                base += tax_amount

            taxes.append({
                'id': tax.id,
                'name': tax.with_context(**{'lang': partner.lang} if partner else {}).name,
                'amount': tax_amount,
                'base': tax_base,
                'sequence': tax.sequence,
                'account_id': tax.account_id.id,
                'refund_account_id': tax.refund_account_id.id,
                'analytic': tax.analytic,
                'price_include': tax.price_include,
                'tax_exigibility': tax.tax_exigibility,
            })

        return {
            'taxes': sorted(taxes, key=lambda k: k['sequence']),
            'total_excluded': currency.round(total_excluded) if round_total else total_excluded,
            'total_included': currency.round(total_included) if round_total else total_included,
            'base': base,
        }
