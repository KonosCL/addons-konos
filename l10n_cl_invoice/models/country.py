# -*- coding: utf-8 -*-
from odoo import fields, models, api


class sii_country(models.Model):
    _inherit = 'res.country'

    rut_natural = fields.Char('RUT persona natural', size=11)
    rut_juridica = fields.Char('RUT persona juridica', size=11)
    rut_otro = fields.Char('RUT otro', size=11)
