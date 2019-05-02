# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Chilean 8 Column Balance',
    'version': '12.0.1.0.0',
    'category': 'Invoicing Management',
    'summary': 'Chilean 8 Column Balance For Odoo 12',
    'sequence': '10',
    'author': 'Konos',
    'company': 'Konos',
    'maintainer': 'Konos',
    'support': 'info@konos.cl',
    'website': '',
    'depends': ['account'],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/account_pdf_reports.xml',
        'views/account_reports_settings.xml',
        'wizards/trial_balance.xml',
        'reports/report.xml',
        'reports/report_trial_balance.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
    'qweb': [],
}
