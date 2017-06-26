# -*- coding: utf-8 -*-
from odoo import fields, models, api


class res_currency(models.Model):
    _inherit = "res.currency"
    _description = "Currency"

    sii_code = fields.Char('SII Code', size=4, readonly=True)
    sii_desc = fields.Char('SII Description', size=250, readonly=True)
    sii_dt_from = fields.Date('SII Valid from', readonly=True)
    