# -*- coding: utf-8 -*-
##############################################################################
# Odoo / OpenERP, Open Source Management Solution
# Copyright (c) 2018 Konos
# Nelson Ramírez Sánchez
# http://konos.cl
#
# Derivative from Odoo / OpenERP / Tiny SPRL
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp

class hr_contract(models.Model):

    _inherit = 'hr.contract'
    _description = 'Employee Contract'
    """
    Employee contract allows to add different values in fields.
    Fields are used in salary rule computation.
    """
    afp_id = fields.Many2one('hr.afp', 'AFP')
    anticipo_sueldo = fields.Float('Anticipo de Sueldo',help="Anticipo De Sueldo Realizado Contablemente")
    carga_familiar = fields.Integer('Carga Simple',help="Carga familiar para el cálculo de asignación familiar simple")
    carga_familiar_maternal = fields.Integer('Carga Maternal',help="Carga familiar para el cálculo de asignación familiar maternal")
    carga_familiar_invalida = fields.Integer('Carga Inválida',help="Carga familiar para el cálculo de asignación familiar inválida")            
    colacion = fields.Float('Asig. Colación', help="Colación")
    isapre_id = fields.Many2one('hr.isapre', 'Nombre')
    isapre_cotizacion_uf = fields.Float('Cotización', digits=(6, 4),  help="Cotización Pactada")  
    isapre_fun = fields.Char('Número de FUN',  help="Indicar N° Contrato de Salud a Isapre")    
    movilizacion = fields.Float('Asig. Movilización', help="Movilización")
    mutual_seguridad = fields.Boolean('Mutual Seguridad', default=True)
    otro_no_imp = fields.Float('Otros No Imponible', help="Otros Haberes No Imponibles")
    otros_imp = fields.Float('Otros Imponible', help="Otros Haberes Imponibles")
    pension = fields.Boolean('Pensionado')
    sin_afp = fields.Boolean('No Calcula AFP')
    sin_afp_sis = fields.Boolean('No Calcula AFP SIS')
    seguro_complementario_id = fields.Many2one('hr.seguro.complementario', 'Nombre')
    seguro_complementario = fields.Float('Cotización',  help="Seguro Complementario")
    viatico_santiago = fields.Float('Asig. Viático',  help="Asignación de Viático")
    complete_name = fields.Char(related='employee_id.firstname')
    last_name = fields.Char(related='employee_id.last_name')
    gratificacion_legal = fields.Boolean('Gratificación L. Manual')
    isapre_moneda= fields.Selection((('uf', 'UF'), ('clp', 'Pesos')), 'Tipo de Moneda', default="uf")
    apv_id = fields.Many2one('hr.apv', 'Nombre')
    aporte_voluntario = fields.Float('Ahorro Previsional Voluntario (APV)', help="Ahorro Previsional Voluntario (APV)")
    aporte_voluntario_moneda= fields.Selection((('uf', 'UF'), ('clp', 'Pesos')), 'Tipo de Moneda', default="uf")
    forma_pago_apv = fields.Selection((('1', 'Directa'), ('2', 'Indirecta')), 'Forma de Pago', default="1")
    seguro_complementario_moneda= fields.Selection((('uf', 'UF'), ('clp', 'Pesos')), 'Tipo de Moneda', default="uf")
    centro_costo_id = fields.Many2one('hr.centroscostos', 'Centros Costos')
