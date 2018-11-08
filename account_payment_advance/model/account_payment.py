# -*- coding: utf-8 -*-
# Copyright 2016 Konos <info@konos.cl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval as eval


class AccountPayment(models.Model):
    _inherit = "account.payment"
    advance_ok = fields.Boolean(
        string='Register advance', 
        help="Select if you want to establish a features of advance")
    advance_account_id = fields.Many2one('account.account',
        string="Account", 
        domain="[('deprecated', '=', False)]",
        help="This account will be used instead of the default one as the receivable account for the current partner")


    @api.one
    @api.depends('invoice_ids', 'payment_type', 'partner_type', 'partner_id')
    def _compute_destination_account_id(self):
        """ inherited and overwrite original method
            Add the condition that evaluates if exists account advance and it placed as has account destiny if condition applied.
        """
        if self.advance_ok and self.advance_account_id:
            self.destination_account_id = self.advance_account_id.id
        else:
            super(AccountPayment, self)._compute_destination_account_id()

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