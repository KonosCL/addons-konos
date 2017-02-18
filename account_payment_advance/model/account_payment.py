# -*- coding: utf-8 -*-
# Copyright 2016 Konos <info@konos.cl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from openerp import api, fields, models, _
from openerp.exceptions import UserError, ValidationError
from openerp.tools.safe_eval import safe_eval as eval


class AccountPayment(models.Model):
    _inherit = "account.payment"
    advance_account_id = fields.Many2one('account.account',
        string="Account", 
        domain="[('deprecated', '=', False)]",
        help="This account will be used instead of the default one as the receivable account for the current partner", 
        required=True)


    @api.one
    @api.depends('invoice_ids', 'payment_type', 'partner_type', 'partner_id')
    def _compute_destination_account_id(self):
        if self.invoice_ids:
            self.destination_account_id = self.invoice_ids[0].account_id.id
        elif self.payment_type == 'transfer':
            if not self.company_id.transfer_account_id.id:
                raise UserError(_('Transfer account not defined on the company.'))
            self.destination_account_id = self.company_id.transfer_account_id.id
        elif self.partner_id:
            if self.partner_type == 'customer':
                self.destination_account_id = self.advance_account_id and self.advance_account_id.id or self.partner_id.property_account_receivable_id.id
            else:
                self.destination_account_id = self.advance_account_id and self.advance_account_id.id or self.partner_id.property_account_payable_id.id



    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.payment_type == 'inbound':
            self.advance_account_id = self.partner_id.property_account_receivable_id.id
        elif self.payment_type == 'outbound':
            self.advance_account_id = self.partner_id.property_account_payable_id.id



    @api.onchange('payment_type')
    def _onchange_payment_type(self):
    	res = self._onchange_partner_id()
        if self.payment_type:
            return {'domain': {'payment_method': [('payment_type', '=', self.payment_type)]}}  
           


