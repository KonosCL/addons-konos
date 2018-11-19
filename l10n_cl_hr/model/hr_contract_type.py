from odoo import api, fields, models, tools, _


class hr_contract_type(models.Model):
    _inherit = 'hr.contract.type'
    _description = 'Tipo de Contrato'

    codigo = fields.Char('Codigo')