# -*- coding: utf-8 -*-
from odoo import api, models, fields, Command, _


class AccountTaxRepartitionLineTemplate(models.Model):
    _inherit = "account.tax.repartition.line.template"

    sii_type = fields.Selection(
        [
            ('N', 'Normal'),
            ('A','Anticipado'),
            ('R','Retención'),
        ],
        string="Tipo de impuesto para el SII",
        default='N',
    )
    credec = fields.Boolean(
        string="Credec"
    )

    def get_repartition_line_create_vals(self, company):
        rslt = [Command.clear()]
        for record in self:
            rslt.append(Command.create({
                'factor_percent': record.factor_percent,
                'repartition_type': record.repartition_type,
                'tag_ids': [Command.set(record._get_tags_to_add().ids)],
                'company_id': company.id,
                'use_in_tax_closing': record.use_in_tax_closing,
                'sii_type': record.sii_type,
                'credec': record.credec,
            }))
        return rslt


class AccountTaxRepartitionLine(models.Model):
    _inherit = "account.tax.repartition.line"

    sii_type = fields.Selection(
        [
            ('N', 'Normal'),
            ('A','Anticipado'),
            ('R','Retención'),
        ],
        string="Tipo de impuesto para el SII",
        default='N',
    )
    credec = fields.Boolean(
        string="Credec"
    )
