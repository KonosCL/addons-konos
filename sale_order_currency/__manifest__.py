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
    'name': 'Cotizaciones de Venta en Otra Moneda',
    'version': '11.0',
    'category': 'Sale',
    'license': 'AGPL-3',
    'summary': 'Cotizaciones de Venta en Otra Moneda',
    'author': 'Konos Soluciones y Servicios Limitada',
    'website': 'http://konos.cl',
    'depends': ['base', 'sale', 'sale_order_dates'],
    'data': [
        'views/sale_views.xml',
    ],
    'installable': True,
}
