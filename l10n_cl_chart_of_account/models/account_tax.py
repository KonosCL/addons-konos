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
    sii_detailed = fields.Boolean(
            string='Desglose de IVA',
            default=False,
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
