# -*- encoding: utf-8 -*-
{
    'name': 'Chilean Payroll with Accounting',
    'author': 'Konos',
    'license': 'AGPL-3',
    'category': 'Localization',
    'depends': ['l10n_cl_hr', 'hr_payroll_account','l10n_cl_chart_of_account'],
    'version': '12.0.0.0',
    'description': """
Chilean Payroll Accounting hooks.
=============================

    * Links Rules to Accounts based on Chilean Accounting Localization
    """,

    'auto_install': False,
    'website': 'https://konos.cl',
    'data':[
        'data/l10n_cl_hr_payroll_account_data.xml',
    ],
    'installable': True
}
