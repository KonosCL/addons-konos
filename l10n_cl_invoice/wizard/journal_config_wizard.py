# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class AccountJournalDocumentConfig(models.TransientModel):
    _name = 'account.journal.document_config'

    debit_notes = fields.Selection(
        [('dont_use', 'Do not use'), ('own_sequence', 'Use')],
        string='Debit Notes', required=True, default='own_sequence')
    credit_notes = fields.Selection(
        [('own_sequence', 'Use')], string='Credit Notes', required=True,
        default='own_sequence')
    dte_register = fields.Boolean(
        'Register Electronic Documents?', default=True, help="""
This option allows you to register electronic documents (DTEs) issued by
MiPyme SII Portal, Third parties services, or by Odoo itself (to register
DTEs issued by Odoo l10n_cl_dte/caf modules are needed.
""")
    non_dte_register = fields.Boolean(
        'Register Manual Documents?')
    electronic_ticket = fields.Boolean(
        'Register Electronic Ticket')
    free_tax_zone = fields.Boolean(
        'Register Free-Tax Zone or # 1057 Resolution Documents?')
    settlement_invoice = fields.Boolean(
        'Register Settlement Invoices?')
    weird_documents = fields.Boolean(
        'Unusual Documents', help="""
Include unusual taxes documents, as transfer invoice, and reissue
""")
#        'excempt_documents': fields.boolean(
#            'VAT Excempt Invoices', readonly=True,
#            default='_get_journal_excempt'),

    other_available = fields.Boolean(
        'Others available?', default='_get_other_avail')

    @api.model
    def _get_other_avail(self):
        return True

    # @api.model
    # def _get_journal_excempt(self):
    #     return True

    def confirm(self, context=None):
        """
        Confirm Configure button
        """
        if context is None:
            context = {}

        journal_ids = context.get('active_ids', False)
        wizard = self.browse()
        # self.create_journals(journal_ids, wizard)
        self.create_journals(journal_ids)

    def create_journals(self, journal_ids):
        for journal in self.env['account.journal'].browse(journal_ids):
            responsability = journal.company_id.responsability_id
            if not responsability.id:
                raise UserError(
                    _('Your company has not setted any responsability. Please, \
set your company responsability in the company partner before continue.'))
            journal_type = journal.type
            if journal_type in ['sale', 'sale_refund']:
                letter_ids = [x.id for x in responsability.issued_letter_ids]
            elif journal_type in ['purchase', 'purchase_refund']:
                letter_ids = [x.id for x in responsability.received_letter_ids]
            if journal_type == 'sale':
                for doc_type in ['invoice', 'debit_note']:
                    self.create_journal_document(
                        letter_ids, doc_type, journal.id)
            elif journal_type == 'purchase':
                for doc_type in ['invoice', 'debit_note', 'invoice_in']:
                    self.create_journal_document(
                        letter_ids, doc_type, journal.id)
                    # self.create_journal_document(
                    # cr, uid, letter_ids, doc_type, journal.id,
                    # non_dte_register, dte_register, settlement_invoice,
                    # free_tax_zone, credit_notes, debit_notes, context)
            elif journal_type in ['sale_refund', 'purchase_refund']:
                _logger.info('notas de credito de compra o venta')
                self.create_journal_document(
                    letter_ids, 'credit_note', journal.id)

    def create_sequence(self, name, journal):
        vals = {
            'name': journal.name + ' - ' + name,
            'padding': 6}
        sequence_obj = self.env['ir.sequence']
        sequence_id = sequence_obj.sudo().create(vals)
        # sequence_id = self.env['ir.sequence'].create(vals)
        return sequence_id

    def create_journal_document(
            self, letter_ids, document_type, journal_id):
        _logger.info(document_type, letter_ids)
        if_zf = [] if self.free_tax_zone else [901, 906, 907]
        if_lf = [] if self.settlement_invoice else [40, 43]
        if_tr = [] if self.weird_documents else [29, 108, 914, 911, 904, 905]
        # if_pr = [] if self.purchase_invoices else [45, 46]
        journal = self.env['account.journal'].browse(
            journal_id)
        if_na = [] if journal.excempt_documents else [32, 34]
        dt_types_exclude = if_zf + if_lf + if_tr + if_na
        _logger.info(dt_types_exclude)

        document_class_obj = self.env['sii.document_class']
        document_class_ids = document_class_obj.search([
                ('document_letter_id', 'in', letter_ids),
                ('document_type', '=', document_type),
                ('sii_code', 'not in', dt_types_exclude)])
        # raise UserError(
        #     'letter_ids: {}, document_type: {}, sii_code not in: {},
        # document_class_ids: {}'.format(
        #     letter_ids,
        #     document_type,
        #     dt_types_exclude,
        #     document_class_ids))

        # raise UserError(document_class_obj.browse(document_class_ids))

        journal_document_obj = self.env['account.journal.sii_document_class']
        sequence = 10
        for document_class_id in document_class_ids:
            doc_class = document_class_obj.browse(document_class_id.id)
            if not doc_class.dte:
                _logger.info('documento manual: ')
                if self.non_dte_register:
                    _logger.info('non dte')
                else:
                    continue
            else:
                _logger.info('documento electronico')
                if self.dte_register:
                    _logger.info('dte')
                    pass
                else:
                    continue
            _logger.info('crear')
            sequence_id = self.create_sequence(doc_class.name, journal)
            vals = {
                'sii_document_class_id': doc_class.id,
                'sequence_id': sequence_id.id,
                'journal_id': journal.id,
                'sequence': sequence}
            journal_document_obj.create(vals)
            sequence += 10
