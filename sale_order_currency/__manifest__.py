# -*- coding: utf-8 -*-
##############################################################################
#
#    
#    
#    Copyright (C) 2018 Konos (http://www.konos.cl)
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
    'name': 'Sale Order Currency',
    'version': '11.0.1',
    'category': 'Sale',
    'license': 'AGPL-3',
    'summary': 'Converts the amount and currency in the sale order into the local currency',
    'author': u'Konos, Daniel Santibáñez Polanco',
    'website': 'http://konos.cl',
    'depends': ['base', 'sale', 'account'],
    'data': [
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
