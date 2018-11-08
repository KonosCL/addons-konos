from odoo import api, fields, models, tools, _


class hr_apv(models.Model):
    _name = 'hr.apv'
    _description = 'Institución Autorizada APV - APVC : Cias Seguros de Vida'
    codigo = fields.Char('Codigo', required=True)
    name = fields.Char('Nombre', required=True)
