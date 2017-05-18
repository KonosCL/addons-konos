# -*- coding: utf-8 -*-

{
    'name': "Delete payroll",

    'summary': """
        Delete payroll in done state""",

    'description': """
        This module allow for user account Adviser can delete payroll in done state, add button delete
        payroll and remove account_move
    """,

    'author': "Marcos Organizador de Negocios SRL - Write by Eneldo Serrata",
    'website': "http://marcos.do",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_payroll', "hr_payroll_account", 'account_cancel'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}