# -*- coding: utf-8 -*-
from odoo import api, models, fields, _


class AccountTaxRepartitionLineTemplate(models.Model):
    _inherit = "account.tax.repartition.line.template"

    sii_type = fields.Selection(
        [
            ('A','Anticipado'),
            ('R','Retención'),
        ],
        string="Tipo de impuesto para el SII",
    )

    def get_repartition_line_create_vals(self, company):
        rslt = [(5, 0, 0)]
        for record in self:
            tags_to_add = self.env['account.account.tag']
            tags_to_add += record.plus_report_line_ids.mapped('tag_ids').filtered(lambda x: not x.tax_negate)
            tags_to_add += record.minus_report_line_ids.mapped('tag_ids').filtered(lambda x: x.tax_negate)
            tags_to_add += record.tag_ids

            rslt.append((0, 0, {
                'factor_percent': record.factor_percent,
                'repartition_type': record.repartition_type,
                'tag_ids': [(6, 0, tags_to_add.ids)],
                'company_id': company.id,
                'use_in_tax_closing': record.use_in_tax_closing,
                'sii_type': record.sii_type
            }))
        return rslt


class AccountTaxRepartitionLine(models.Model):
    _inherit = "account.tax.repartition.line"

    sii_type = fields.Selection(
        [
            ('A','Anticipado'),
            ('R','Retención'),
        ],
        string="Tipo de impuesto para el SII",
    )
