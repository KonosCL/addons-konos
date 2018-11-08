from odoo import api, fields, models, tools, _


class hr_seguro_complementario(models.Model):
    _name = 'hr.seguro.complementario'
    _description = 'Seguro Complementario'
    
    codigo = fields.Char('Codigo', required=True)
    name = fields.Char('Nombre', required=True)
