# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (c) 2017 Konos http://www.konos.cl

from openerp import SUPERUSER_ID
from openerp.addons import account

def _auto_install_l10n(cr, registry):
    #check the country of the main company (only) and eventually load some module needed in that country
    country_code = registry['res.users'].browse(cr, SUPERUSER_ID, SUPERUSER_ID, {}).company_id.country_id.code
    if country_code:
        #auto install localization module(s) if available
        module_list = []
        if country_code in ['BJ', 'BF', 'CM', 'CF', 'KM', 'CG', 'CI', 'GA', 'GN', 'GW', 'GQ', 'ML', 'NE', 'CD', 'SN', 'TD', 'TG']:
            #countries using OHADA Chart of Accounts
            module_list.append('l10n_syscohada')
        elif country_code == 'GB':
            module_list.append('l10n_uk')
        else:
            if country_code.lower() == 'cl' and registry['ir.module.module'].search(cr, SUPERUSER_ID, [('name', '=', 'l10n_cl_chart_of_account')]):
                module_list.append('l10n_cl_chart_of_account')
            elif registry['ir.module.module'].search(cr, SUPERUSER_ID, [('name', '=', 'l10n_' + country_code.lower())]):
                module_list.append('l10n_' + country_code.lower())
            else:
                module_list.append('l10n_generic_coa')
        if country_code == 'US':
            module_list.append('account_plaid')
            module_list.append('account_check_printing')
        if country_code in ['US', 'AU', 'NZ', 'CA', 'CO', 'EC', 'ES', 'FR', 'IN', 'MX', 'UK']:
            module_list.append('account_yodlee')

        #european countries will be using SEPA
        europe = registry['ir.model.data'].xmlid_to_object(cr, SUPERUSER_ID, 'base.europe', raise_if_not_found=False, context={})
        if europe:
            europe_country_codes = [x.code for x in europe.country_ids]
            if country_code in europe_country_codes:
                module_list.append('account_sepa')
        module_ids = registry['ir.module.module'].search(cr, SUPERUSER_ID, [('name', 'in', module_list), ('state', '=', 'uninstalled')])
        registry['ir.module.module'].button_install(cr, SUPERUSER_ID, module_ids, {})
        
#mokeypatch para reemplazar funcion y al ser chile instale este paquete contable en lugar del original
account._auto_install_l10n = _auto_install_l10n