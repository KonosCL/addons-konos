# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Chilean Payroll',
    'category': 'Localization',
    'author': 'Konos, '
              u'''Blanco Martin & Asociados''',
    'license': 'AGPL-3',
    'depends': ['hr_payroll'],
    'contributors': [
        "Nelson Ramirez <info@konos.cl>",
        "Daniel Blanco Martn <daniel@blancomartin.com>",
    ],
    'license': 'AGPL-3',
    'version': '10.0.3',
    'description': """
Chilean Payroll Salary Rules.
============================

    -Configuration of hr_payroll for Chile localization.
    -All main contributions rules for Chile payslip.
    * New payslip report
    * Employee Contracts
    * Allow to configure Basic / Gross / Net Salary
    * Attendance, Holidays and Sick Licence   
    * Employee PaySlip
    * Allowance / Deduction
    * Pention Chilean Indicators
    * Libro de Remuneraciones 
    * Previred Plain Text
    , ...
    Report
    """,
    'active': True,
    'data': [
        'views/hr_indicadores_previsionales_view.xml',
        'views/hr_salary_rule_view.xml',
        'views/hr_contract_view.xml',
        'views/hr_employee.xml',
        'views/hr_payslip_view.xml',
        'views/hr_afp_view.xml',
        'views/hr_payslip_run_view.xml',
        'views/hr_contribution_register_view.xml',
        'views/report_payslip.xml',
        'views/report_hrsalarybymonth.xml',
        'views/hr_salary_books.xml',
        'data/l10n_cl_hr_payroll_data.xml',
    ],
    'demo': ['demo/l10n_cl_hr_payroll_demo.xml'],
    'installable': True,
    'application': False,
    'auto_install': False
}

