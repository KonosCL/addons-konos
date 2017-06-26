# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval as eval
from odoo.exceptions import UserError


class AccountInvoiceRefund(models.TransientModel):
    """Refunds invoice"""

    _inherit = "account.invoice.refund"

    tipo_nota = fields.Many2one(
        'sii.document_class', string="Tipo De nota", required=True,
        domain=[('document_type', 'in', ['debit_note', 'credit_note']),
                ('dte', '=', True)])
    filter_refund = fields.Selection([
                ('1', 'Anula Documento de Referencia'),
                ('2', 'Corrige texto Documento Referencia'),
                ('3', 'Corrige montos')], default='1', string='Refund Method',
        required=True,
        help='Refund base on this type. You can not Modify and Cancel if the \
invoice is already reconciled')

    @api.multi
    def compute_refund(self, mode='refund'):
        inv_obj = self.env['account.invoice']
        inv_tax_obj = self.env['account.invoice.tax']
        inv_line_obj = self.env['account.invoice.line']
        inv_reference_obj = self.env['account.invoice.referencias']
        context = dict(self._context or {})
        xml_id = False
        for form in self:
            created_inv = []
            date = False
            description = False
            tipo_nota = form.tipo_nota
            for inv in inv_obj.browse(context.get('active_ids')):
                if inv.state in ['draft', 'proforma2', 'cancel']:
                    raise UserError(
                        _('Cannot refund draft/proforma/cancelled invoice.'))
                if inv.reconciled and inv.amount_total > 0:
                    raise UserError(
                        _('Cannot refund invoice which is already reconciled, \
invoice should be unreconciled first. You can only refund this invoice.'))

                date = form.date or False
                description = form.description or inv.name
                if mode in ['2']:
                    invoice = inv.read(
                        ['name', 'type', 'number', 'reference', 'comment',
                         'date_due', 'partner_id', 'partner_insite',
                         'partner_contact', 'partner_ref', 'payment_term_id',
                         'account_id', 'currency_id', 'invoice_line_ids',
                         'journal_id', 'date'])
                    invoice = invoice[0]
                    del invoice['id']
                    prod = self.env['product.product'].search(
                        [('product_tmpl_id', '=', self.env.ref(
                            'l10n_cl_invoice.no_product').id)])
                    account = inv.invoice_line_ids.get_invoice_line_account(
                        inv.type, prod, inv.fiscal_position_id, inv.company_id)
                    invoice.update(
                        {'date_invoice': date, 'state': 'draft',
                         'number': False, 'invoice_line_ids': [[5, ], [0, 0, {
                            'product_id': prod.id, 'account_id': account.id,
                            'name': prod.name, 'quantity': 0,
                            'price_unit': 0}]],
                         'date': date,
                         'name': description,
                         'origin': inv.origin})
                    for field in (
                            'partner_id', 'account_id', 'currency_id',
                            'payment_term_id', 'journal_id'):
                        invoice[field] = invoice[field] and invoice[field][0]
                        refund = inv_obj.create(invoice)
                        if refund.payment_term_id.id:
                            refund._onchange_payment_term_date_invoice()
                elif mode in ['1', '3']:
                    refund = inv.refund(
                        form.date_invoice, date, description, inv.journal_id.id)
                    refund.compute_taxes()
                type = inv.type
                if inv.type in ['out_invoice', 'out_refund']:
                    refund.type = 'out_refund'
                elif inv.type in ['in_invoice', 'in_refund']:
                    refund.type = 'in_refund'
                # refund._get_available_journal_document_class(tipo_nota.id)
                refund._get_available_journal_document_class()
                created_inv.append(refund.id)
                refund.update({
                    'turn_issuer': inv.turn_issuer.id,})
                if inv.type in ['out_invoice', 'out_refund']:
                    refund.update(
                        {'referencias': [[5, ], [0, 0, {
                            'origen': int(inv.sii_document_number),
                            'sii_referencia_TpoDocRef':
                                inv.sii_document_class_id.id,
                            'sii_referencia_CodRef': mode,
                            'motivo': description,
                            'fecha_documento': inv.date_invoice}]]})
                xml_id = (inv.type in ['out_refund', 'out_invoice']) and \
                    'action_invoice_tree1' or (inv.type in [
                    'in_refund', 'in_invoice']) and 'action_invoice_tree2'
                # Put the reason in the chatter
                subject = _("Invoice refund")
                body = description
                refund.message_post(body=body, subject=subject)
        if xml_id:
            result = self.env.ref('account.%s' % (xml_id)).read()[0]
            invoice_domain = eval(result['domain'])
            invoice_domain.append(('id', 'in', created_inv))
            result['domain'] = invoice_domain
            return result
        return True
