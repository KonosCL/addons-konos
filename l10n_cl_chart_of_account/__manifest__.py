# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (c) 2017 Konos Soluciones y Servicios Limitada http://www.konos.cl

{
    'name': 'Chile Localization Chart Account SII',
    'version': '1.1',
    'description': """
Chilean accounting chart and tax localization.
==============================================
Plan contable chileno e impuestos de acuerdo a disposiciones vigentes,
basado en plan de cuentas del Servicio de Impuestos Internos

    """,
    'author': 'Konos',
    'website': 'http://www.konos.cl',
    'category': 'Localization',
    'depends': ['account'],
    'data': [
            'views/account_tax.xml',
            'data/l10n_cl_chart_of_account_data.xml',
            'data/account_tax_data.xml',
            'data/account_chart_template_data.yml',
    ],
}
