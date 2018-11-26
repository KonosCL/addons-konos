# -*- coding: utf-8 -*-
# Part of Konos. See LICENSE file for full copyright and licensing details.

{
    'name': 'Import Chilean Bank Statement Lines from Excel/CSV file ',
    'version': '11.0.0.3',
    'summary': 'This module helps you to import chilean bank statement line on Odoo using Excel and CSV file',
    'description': """
	Import Bank Statement Lines from Excel
    """,
    'author': 'Konos',
    'website': 'http://www.konos.cl',
    'category': 'Localization/Chile',
    'depends': ['account'],
    'data': ["views/bank_statement.xml",
             "wizard/transit_payment_export.xml",
             ],
	'qweb': [
		],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    "images":['static/description/Banner.png'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
