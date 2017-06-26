# -*- coding: utf-8 -*-
from odoo import fields, models


class res_company(models.Model):
    _inherit = "res.company"

    responsability_id = fields.Many2one(
        related='partner_id.responsability_id',
        relation='sii.responsability',
        string="Responsability",)
    start_date = fields.Date(
        related='partner_id.start_date',
        string='Start-up Date',)
    invoice_vat_discrimination_default = fields.Selection(
        [('no_discriminate_default', 'Yes, No Discriminate Default'),
         ('discriminate_default', 'Yes, Discriminate Default')],
        'Invoice VAT discrimination default',
        default='no_discriminate_default',
        required=True,
        help="""Define behaviour on invoices reports. Discrimination or not \
        will depend in partner and company responsability and SII letters\
        setup:
            * If No Discriminate Default, if no match found it won't \
            discriminate by default.
            * If Discriminate Default, if no match found it would \
            discriminate by default.
            """)
    tp_sii_code = fields.Char(
        'Tax Payer SII Code', related='partner_id.tp_sii_code', readonly=True)

