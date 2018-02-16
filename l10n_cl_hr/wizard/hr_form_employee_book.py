# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution Chilean Payroll
#
#    Copyright (c) 2017 Blanco Martin y Asociados - Nelson Ramírez Sánchez
#    Daniel Blanco
#    http://blancomartin.cl
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import api, fields, models
import time


class hr_salary_employee_bymonth(models.TransientModel):

    _name = 'hr.salary.employee.month'
    _description = 'Libro de Remuneraciones Haberes'

    def _get_default_end_date(self):
        date = fields.Date.from_string(fields.Date.today())
        return date.strftime('%Y') + '-' + date.strftime('%m') + '-' + date.strftime('%d')

    end_date = fields.Date(string='End Date', required=True, default=_get_default_end_date)


    @api.multi
    def print_report(self):
        """
         To get the date and print the report
         @return: return report
        """
        self.ensure_one()
        data = {'ids': self.env.context.get('active_ids', [])}
        res = self.read()
        res = res and res[0] or {}
        data.update({'form': res})
        return self.env.ref('l10n_cl_hr.hr_salary_books').report_action(self, data=data)
