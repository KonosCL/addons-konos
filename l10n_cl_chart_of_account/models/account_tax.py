# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
import math


class AccountTaxTemplate(models.Model):
    _inherit = 'account.tax.template'

    sii_code = fields.Integer(
            string='SII Code',
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
