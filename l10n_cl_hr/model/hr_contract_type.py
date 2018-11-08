from odoo import api, fields, models, tools, _


class hr_contract_type(models.Model):
    _inherit = 'hr.contract.type'
    _description = 'Contract Type'
    
    codigo = fields.Char('Codigo')
