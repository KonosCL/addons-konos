# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution Chilean Payroll
#
#    Copyright (c) 2017 Konos
#    http://konos.cl
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

import time
from odoo import models, api


class report_hr_salary_employee_bymonth(models.AbstractModel):
    _name = 'report.l10n_cl_hr.report_hrsalarybymonth'

    @api.model
    def get_report_values(self, docids, data=None):

        return {
            'time': time,
            'get_employee': self.get_employee,
            'get_employee2': self.get_employee2,
            'get_analytic': self.get_analytic,
            'mnths': [],
            'mnths_total': [],
            'total': 0.0,
        }

    def get_worked_days(self, form, emp_id, emp_salary, mes, ano):

        self.cr.execute(
            '''select sum(number_of_days) from hr_payslip_worked_days as p
left join hr_payslip as r on r.id = p.payslip_id
where r.employee_id = %s  and (to_char(date_to,'mm')= %s)
and (to_char(date_to,'yyyy')= %s) and ('WORK100' = p.code)
''', (emp_id, mes, ano,))

        max = self.cr.fetchone()

        if max is None:
            emp_salary.append(0.00)
        elif  3>max[0]:
            emp_salary.append(max[0])
        else:
            self.cr.execute(
            '''select number_of_days from hr_payslip_worked_days as p
left join hr_payslip as r on r.id = p.payslip_id
where r.employee_id = %s  and (to_char(date_to,'mm')= %s)
and (to_char(date_to,'yyyy')= %s) and (('No_Trabajado' = p.code) or ('Licencia' = p.code))
group by number_of_days''', (emp_id, mes, ano,))
            max = self.cr.fetchone()
            try:
                emp_salary.append(30 - max[0])
            except:
                emp_salary.append(30.00)


        return emp_salary

    def get_employe_basic_info(self, emp_salary, cod_id, mes, ano):

        self.cr.execute(
            '''select sum(pl.total) from hr_payslip_line as pl
left join hr_payslip as p on pl.slip_id = p.id
left join hr_employee as emp on emp.id = p.employee_id
left join resource_resource as r on r.id = emp.resource_id
where p.state = 'done' and (pl.code like %s) and (to_char(p.date_to,'mm')=%s)
and (to_char(p.date_to,'yyyy')=%s)
group by r.name, p.date_to''', (cod_id, mes, ano,))

        max = self.cr.fetchone()

        if max is None:
            emp_salary.append(0.00)
        else:
            emp_salary.append(max[0])

        return emp_salary

    def get_analytic(self, form):
        emp_salary = []
        salary_list = []
        last_year = form['end_date'][0:4]
        last_month = form['end_date'][5:7]
        cont = 0

        self.cr.execute(
            '''select sum(pl.total), w.name from hr_payslip_line as pl
left join hr_payslip as p on pl.slip_id = p.id
left join hr_employee as emp on emp.id = p.employee_id
left join hr_contract as r on r.id = p.contract_id
left join account_analytic_account as w on w.id = r.analytic_account_id
where p.state = 'done' and (to_char(p.date_to,'mm')=%s)
and (to_char(p.date_to,'yyyy')=%s)
group by w.name order by name''', (last_month, last_year,))

        id_data = self.cr.fetchall()
        if id_data is None:
            emp_salary.append(0.00)
            emp_salary.append(0.00)

        else:
            for index in id_data:
                emp_salary.append(id_data[cont][0])
                emp_salary.append(id_data[cont][1])

                cont = cont + 1
                salary_list.append(emp_salary)

                emp_salary = []

        return salary_list

    def get_salary(self, emp_id, emp_salary, cod_id, mes, ano):

        self.cr.execute(
            '''select sum(pl.total) from hr_payslip_line as pl
left join hr_payslip as p on pl.slip_id = p.id
left join hr_employee as emp on emp.id = p.employee_id
left join resource_resource as r on r.id = emp.resource_id
where p.state = 'done' and p.employee_id = %s and (pl.code like %s)
and (to_char(p.date_to,'mm')=%s) and (to_char(p.date_to,'yyyy')=%s)
group by r.name, p.date_to,emp.id''', (emp_id, cod_id, mes, ano,))

        max = self.cr.fetchone()

        if max is None:
            emp_salary.append(0.00)
        else:
            emp_salary.append(max[0])

        return emp_salary

    def get_employee2(self, form):
        emp_salary = []
        salary_list = []
        last_year = form['end_date'][0:4]
        last_month = form['end_date'][5:7]
        cont = 0

        self.cr.execute(
            '''select emp.id, emp.identification_id, emp.firstname, emp.middle_name, emp.last_name, emp.mothers_name
from hr_payslip as p left join hr_employee as emp on emp.id = p.employee_id
left join hr_contract as r on r.id = p.contract_id
where p.state = 'done'  and (to_char(p.date_to,'mm')=%s)
and (to_char(p.date_to,'yyyy')=%s)
group by emp.id, emp.name_related, emp.middle_name, emp.last_name, emp.mothers_name, emp.identification_id
order by last_name''', (last_month, last_year,))

        id_data = self.cr.fetchall()
        if id_data is None:
            emp_salary.append(0.00)
            emp_salary.append(0.00)
            emp_salary.append(0.00)
            emp_salary.append(0.00)
            emp_salary.append(0.00)
        else:
            for index in id_data:
                emp_salary.append(id_data[cont][0])
                emp_salary.append(id_data[cont][1])
                emp_salary.append(id_data[cont][2])
                emp_salary.append(id_data[cont][3])
                emp_salary.append(id_data[cont][4])
                emp_salary.append(id_data[cont][5])
                emp_salary = self.get_worked_days(
                    form, id_data[cont][0], emp_salary, last_month, last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'SUELDO', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'HEX%', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'GRAT', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'BONO', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'TOTIM', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'ASIGFAM', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'TOTNOI', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'TOTNOI', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'HAB', last_month, last_year)

                cont = cont + 1
                salary_list.append(emp_salary)

                emp_salary = []

        return salary_list

    def get_employee(self, form):
        emp_salary = []
        salary_list = []
        last_year = form['end_date'][0:4]
        last_month = form['end_date'][5:7]
        cont = 0

        self.cr.execute(
            '''select emp.id, emp.identification_id, emp.firstname, emp.middle_name, emp.last_name, emp.mothers_name
from hr_payslip as p left join hr_employee as emp on emp.id = p.employee_id
left join hr_contract as r on r.id = p.contract_id
where p.state = 'done'  and (to_char(p.date_to,'mm')=%s)
and (to_char(p.date_to,'yyyy')=%s)
group by emp.id, emp.name_related, emp.middle_name, emp.last_name, emp.mothers_name, emp.identification_id
order by last_name''', (last_month, last_year))

        id_data = self.cr.fetchall()
        if id_data is None:
            emp_salary.append(0.00)
            emp_salary.append(0.00)
            emp_salary.append(0.00)
            emp_salary.append(0.00)
            emp_salary.append(0.00)
        else:
            for index in id_data:
                emp_salary.append(id_data[cont][0])
                emp_salary.append(id_data[cont][1])
                emp_salary.append(id_data[cont][2])
                emp_salary.append(id_data[cont][3])
                emp_salary.append(id_data[cont][4])
                emp_salary.append(id_data[cont][5])
                emp_salary = self.get_worked_days(
                    form, id_data[cont][0], emp_salary, last_month, last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'PREV', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'SALUD', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'IMPUNI', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'SECE', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'ADISA', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'TODELE', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'SMT', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'TDE', last_month,
                    last_year)
                emp_salary = self.get_salary(
                    id_data[cont][0], emp_salary, 'LIQ', last_month,
                    last_year)

                cont = cont + 1
                salary_list.append(emp_salary)

                emp_salary = []

        return salary_list


class wrapped_report_employee_salary_bymonth(models.AbstractModel):
    _name = 'report.l10n_cl_hr.report_hrsalarybymonth'
    #_inherit = 'report.abstract_report'
    _template = 'l10n_cl_hr.report_hrsalarybymonth'
    _wrapped_report_class = report_hr_salary_employee_bymonth

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
