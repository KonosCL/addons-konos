# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Author: Naresh Soni
#    Copyright 2016 Cozy Business Solutions Pvt.Ltd
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
    "name": "Auto Reset Sequences",
     "version": "1.0",
     "author": "Cozy Business Solutions Pvt.Ltd.",
     "website":"www.cozybizs.com",
    "category": "Tools",
    "summary": "Auto reset sequences",
    "description": """

 This module will auto reset the sequences monthly or yearly as configured.

""",
    "depends": ["base","account"],
    "data": ["auto_reset_cron.xml","auto_reset_sequence.xml"],
    "price":9,
    "currency":"EUR",
    "auto_install": False,
    "installable":True
}

