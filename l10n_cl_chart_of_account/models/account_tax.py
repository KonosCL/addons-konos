# -*- coding: utf-8 -*-
from odoo import api, models, fields, _

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
