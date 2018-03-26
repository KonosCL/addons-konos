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

class hr_payslip_employees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    @api.multi
    def compute_sheet(self):
        indicadores_id = False
        if self.env.context.get('active_id'):
            indicadores_id = self.env['hr.payslip.run'].browse(self.env.context.get('active_id')).indicadores_id.id
        return super(hr_payslip_employees, self.with_context(indicadores_id=indicadores_id)).compute_sheet()

