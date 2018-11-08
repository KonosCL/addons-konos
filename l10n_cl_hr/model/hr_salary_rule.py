from odoo import api, fields, models, tools, _


class hr_salary_rule(models.Model):
    _inherit = 'hr.salary.rule'
    _description = 'Salary Rule'
    
    date_start = fields.Date('Fecha Inicio',  help="Fecha de inicio de la regla salarial")
    date_end = fields.Date('Fecha Fin',  help="Fecha del fin de la regla salarial")
