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
    'name': 'Chilean Payroll & Human Resources',
    'category': 'Localization',
    'author': 'Konos, '
              u'''Blanco Martin & Asociados''',
    'website': 'http://konos.cl',
    'license': 'AGPL-3',
    'depends': ['hr_payroll'],
    'contributors': [
        "Nelson Ramirez <info@konos.cl>",
        "Daniel Blanco Martn <daniel@blancomartin.com>",
        "Carlos Lopez Mite <celm1990@hotmail.com>",
    ],
    'license': 'AGPL-3',
    'version': '10.0.9',
    'description': """
Chilean Payroll Salary Rules.
============================

    -Payroll configuration for Chile localization.
    -All contributions rules for Chile payslip.
    * Employee Basic Info
    * Employee Contracts
    * Attendance, Holidays and Sick Licence   
    * Employee PaySlip
    * Allowances / Deductions / Company Inputs
    * Extra Time
    * Pention Chilean Indicators
    * Payroll Books 
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
        'wizard/wizard_export_csv_previred_view.xml',
    ],
    'demo': ['demo/l10n_cl_hr_payroll_demo.xml'],
    'installable': True,
    'application': False,
    'auto_install': False
}

