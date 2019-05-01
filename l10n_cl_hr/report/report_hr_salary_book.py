import time
from odoo import models, api
from odoo.exceptions import UserError, ValidationError

class report_hr_salary_employee_bymonth(models.AbstractModel):
    _name = 'report.l10n_cl_hr.report_hrsalarybymonth'
    _description = 'Monthly Salary Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        get_employee2 = self.get_employee2(data['form'])
        get_employee = self.get_employee(data['form'])
        get_analytic = self.get_analytic(data['form'])
        return {
                'docids':docids,
                'doc_model': model,
                'data': data,
                'docs': docs,
                'time': time,
                'get_employee': get_employee,
                'get_employee2': get_employee2,
                'get_analytic': get_analytic,
                'mnths': [],
                'mnths_total': [],
                'total': 0.0,
                'company_id': self.env.user.company_id,
        }

    def get_worked_days(self, form, emp_id, emp_salary, mes, ano):

        self.env.cr.execute(
            '''select sum(number_of_days) from hr_payslip_worked_days as p
left join hr_payslip as r on r.id = p.payslip_id
where r.employee_id = %s  and (to_char(date_to,'mm')= %s)
and (to_char(date_to,'yyyy')= %s) and ('WORK100' = p.code)
''', (emp_id, mes, ano,))

        max = self.env.cr.fetchone()
        if max[0] is None:
            emp_salary.append(0.00)
        else:
            emp_salary.append(max[0])
        return emp_salary

    def get_employe_basic_info(self, emp_salary, cod_id, mes, ano):

        self.env.cr.execute(
            '''select sum(pl.total) from hr_payslip_line as pl
left join hr_payslip as p on pl.slip_id = p.id
left join hr_employee as emp on emp.id = p.employee_id
left join resource_resource as r on r.id = emp.resource_id
where p.state = 'done' and (pl.code like %s) and (to_char(p.date_to,'mm')=%s)
and (to_char(p.date_to,'yyyy')=%s)
group by r.name, p.date_to''', (cod_id, mes, ano,))

        max = self.env.cr.fetchone()

        try:
            emp_salary.append(max[0])
        except:
            emp_salary.append(0.00)  
        return emp_salary

    def get_centro_costo(self, id):
        valor = "01"
        lineas = self.env['account.analytic.account']
        detalle = lineas.search([('id','=',id)], limit=1)
        if detalle:
            valor = detalle.code
        return valor  

    def get_analytic(self, form):
        emp_salary = []
        salary_list = []
        last_year = form['end_date'][0:4]
        last_month = form['end_date'][5:7]
        cont = 0

        self.env.cr.execute(
            '''select sum(pl.total), w.name from hr_payslip_line as pl
left join hr_payslip as p on pl.slip_id = p.id
left join hr_employee as emp on emp.id = p.employee_id
left join hr_contract as r on r.id = p.contract_id
left join account_analytic_account as w on w.id = r.analytic_account_id
where p.state = 'done' and (to_char(p.date_to,'mm')=%s)
and (to_char(p.date_to,'yyyy')=%s)
group by w.name order by name''', (last_month, last_year,))

        id_data = self.env.cr.fetchall()
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

        self.env.cr.execute(
            '''select sum(pl.total) from hr_payslip_line as pl
left join hr_payslip as p on pl.slip_id = p.id
left join hr_employee as emp on emp.id = p.employee_id
left join resource_resource as r on r.id = emp.resource_id
where p.state = 'done' and p.employee_id = %s and (pl.code like %s)
and (to_char(p.date_to,'mm')=%s) and (to_char(p.date_to,'yyyy')=%s)
group by r.name, p.date_to,emp.id''', (emp_id, cod_id, mes, ano,))

        max = self.env.cr.fetchone()

        try:
            emp_salary.append(max[0])
        except:
            emp_salary.append(0.00)

        return emp_salary

    def get_employee2(self, form):
        emp_salary = []
        salary_list = []
        last_year = form['end_date'][0:4]
        last_month = form['end_date'][5:7]
        cont = 0

        self.env.cr.execute(
            '''select emp.id, emp.identification_id, emp.firstname, emp.middle_name, emp.last_name, emp.mothers_name, r.analytic_account_id
from hr_payslip as p left join hr_employee as emp on emp.id = p.employee_id
left join hr_contract as r on r.id = p.contract_id
where p.state = 'done'  and (to_char(p.date_to,'mm')=%s)
and (to_char(p.date_to,'yyyy')=%s)
group by emp.id, emp.name, emp.middle_name, emp.last_name, emp.mothers_name, emp.identification_id, r.analytic_account_id
order by r.analytic_account_id, last_name''', (last_month, last_year,))

        id_data = self.env.cr.fetchall()
        if id_data is None:
            emp_salary.append(0.00)
            emp_salary.append(0.00)
            emp_salary.append(0.00)
            emp_salary.append(0.00)
            emp_salary.append(0.00)
        else:
            for index in id_data:
                #0 CENTRO DE COSTO 1 RUT 2 PRIMER 3 SEGUNDO 4 APELLIDO 5 SEGUNDO APELLIDO 
                emp_salary.append(self.get_centro_costo(id_data[cont][6]))
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

        self.env.cr.execute(
            '''select emp.id, emp.identification_id, emp.firstname, emp.middle_name, emp.last_name, emp.mothers_name, r.analytic_account_id
from hr_payslip as p left join hr_employee as emp on emp.id = p.employee_id
left join hr_contract as r on r.id = p.contract_id
where p.state = 'done'  and (to_char(p.date_to,'mm')=%s)
and (to_char(p.date_to,'yyyy')=%s)
group by emp.id, emp.name, emp.middle_name, emp.last_name, emp.mothers_name, emp.identification_id, r.analytic_account_id
order by r.analytic_account_id, last_name''', (last_month, last_year))

        id_data = self.env.cr.fetchall()
        if id_data is None:
            emp_salary.append(0.00)
            emp_salary.append(0.00)
            emp_salary.append(0.00)
            emp_salary.append(0.00)
            emp_salary.append(0.00)
        else:
            for index in id_data:
                emp_salary.append(self.get_centro_costo(id_data[cont][6]))
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