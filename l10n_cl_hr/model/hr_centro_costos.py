# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

class hr_centroscostos(models.Model):
    _name = 'hr.centroscostos'
    _description = 'Centros Costos'

    name = fields.Char('Código', translate=True ,size=20)
    desc = fields.Char('Descripción', translate=True )