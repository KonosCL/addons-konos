
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (c) 2018 Konos Soluciones y Servicios Limitada http://www.konos.cl
{
    'name':'Chilean 8 Column Balance',
    'description':'Formato de Balance de 8 Columnas para Chile',
    'category': 'Localization/Chile',
    'license': 'AGPL-3',
    'version':'0.1.1',
    'author':'Konos',
    'website':'http://konos.cl',
    'data': [
            'data/report_paperformat.xml',
            'views/layout.xml',
    ],
    'depends': [
                'account',
            ],
}
