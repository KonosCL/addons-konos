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
import time
import logging
from openerp import models, fields, api, _

_logger = logging.getLogger(__name__)

class ir_sequence(models.Model):
    _inherit = "ir.sequence"

    reset_monthly = fields.Boolean('Auto Reset Monthly ?')
    reset_yearly = fields.Boolean('Auto Reset Yearly ?')
    
    @api.model
    def cron_autoreset(self):
        monthly = self.search([('reset_monthly','=',True)])
        if monthly:
            monthly.write({'number_next_actual':1})
            seqs = [l.name for l in monthly]
            _logger.info('Sequences  %s has been reset monthly'%(','.join(seqs)))
        else:
            _logger.info('No sequence to reset monthly!')

        if time.strftime('%m-%d') == '01-01':
            yearly = self.search([('reset_yearly','=',True)])
            if yearly:
                yearly.write({'number_next_actual':1})
                seqs = [l.name for l in yearly]
                _logger.info('Sequences  %s has been reset yearly '%(','.join(seqs)))
        else:
            _logger.info('No sequence to reset yearly!')

        return True 