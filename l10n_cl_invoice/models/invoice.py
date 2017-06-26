# -*- coding: utf-8 -*-
from odoo import osv, models, fields, api, _
from odoo.exceptions import except_orm, UserError
import json

import logging
_logger = logging.getLogger(__name__)

TYPE2JOURNAL = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale_refund',
    'in_refund': 'purchase_refund', }


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.one
    @api.depends(
        'price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id',
        'invoice_id.company_id')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        taxes = False
        total = self.quantity * self.price_unit
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(
                self.price_unit, currency, self.quantity,
                product=self.product_id,
                partner=self.invoice_id.partner_id, discount=self.discount)
        if taxes:
            self.price_subtotal = price_subtotal_signed = taxes[
                'total_excluded']
        else:
            total_discount = total * ((self.discount or 0.0) / 100.0)
            self.price_subtotal = price_subtotal_signed = total - total_discount
        if self.invoice_id.currency_id and self.invoice_id.currency_id != \
                self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.compute(
                price_subtotal_signed, self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign
        self.price_tax_included = taxes['total_included'] if (
            taxes and taxes['total_included'] > total) else total

    price_tax_included = fields.Monetary(
        string='Amount', readonly=True, compute='_compute_price')

class AccountInvoiceTax(models.Model):
    _inherit = "account.invoice.tax"

    def _getNeto(self):
        neto = 0
        for tax in self:
            base = tax.base
            price_tax_included = 0
            # amount_tax +=tax.amount
            for line in tax.invoice_id.invoice_line_ids:
                if tax.tax_id in line.invoice_line_tax_ids and \
                        tax.tax_id.price_include:
                    price_tax_included += line.price_tax_included
            if price_tax_included > 0:
                base = round(
                    price_tax_included / (1 + tax.tax_id.amount / 100))
                iva_round = round(base * (tax.tax_id.amount / 100))
                if round(base + iva_round) != round(price_tax_included):
                    base = int(
                        price_tax_included / (1 + tax.tax_id.amount / 100))
            neto += base
        return neto

    def _compute_base_amount(self):
        included = False
        for tax in self:
            if tax.tax_id.price_include:
                included = True
        if included:
            neto = self._getNeto()
            tax.base = neto
        else:
            super(AccountInvoiceTax, self)._compute_base_amount()


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def _repair_diff(self, move_lines, dif):
        if move_lines[0][2]['currency_id'] != self.company_id.currency_id:
            return move_lines
        total = self.amount_total
        new_lines = []
        for line in move_lines:
            if line[2]['tax_ids'] and not line[2]['tax_line_id']:
                if dif > 0:
                    val = 1
                    dif -= 1
                elif dif < 0:
                    val = -1
                    dif += 1
                else:
                    val = 0
                if line[2]['tax_ids']:
                    for t in line[2]['tax_ids']:
                        imp = self.env['account.tax'].browse(t[1])
                        if imp.amount > 0 and line[2]['debit'] > 0:
                            line[2]['debit'] += val
                        elif imp.amount > 0:
                            line[2]['credit'] += val
            if line[2]['name'] == '/':
                if line[2]['credit'] > 0:
                    line[2]['credit'] = total
                else:
                    line[2]['debit'] = total
            new_lines.append(line)
        if dif != 0:
            new_lines = self._repair_diff(new_lines, dif)
        return new_lines

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        dif = 0
        total = self.amount_total
        for line in move_lines:
            if line[2]['name'] == '/':
                if line[2]['credit'] > 0:
                    dif = total - line[2]['credit']
                else:
                    dif = total - line[2]['debit']
        if dif != 0:
            move_lines = self._repair_diff(move_lines, dif)
        return move_lines

    def _compute_amount(self):
        for inv in self:
            amount_tax = 0
            included = False
            for tax in inv.tax_line_ids:
                if tax.tax_id.price_include:
                    included = True
                amount_tax += tax.amount
            if included:
                neto = inv.tax_line_ids._getNeto()
            else:
                neto = sum(line.price_subtotal for line in inv.invoice_line_ids)
            inv.amount_untaxed = neto
            inv.amount_tax = amount_tax
            inv.amount_total = inv.amount_untaxed + inv.amount_tax
            amount_total_company_signed = inv.amount_total
            amount_untaxed_signed = inv.amount_untaxed
            if inv.currency_id and inv.currency_id != \
                    inv.company_id.currency_id:
                amount_total_company_signed = inv.currency_id.compute(
                    inv.amount_total, inv.company_id.currency_id)
                amount_untaxed_signed = inv.currency_id.compute(
                    inv.amount_untaxed, inv.company_id.currency_id)
            sign = inv.type in ['in_refund', 'out_refund'] and -1 or 1
            inv.amount_total_company_signed = amount_total_company_signed * sign
            inv.amount_total_signed = inv.amount_total * sign
            inv.amount_untaxed_signed = amount_untaxed_signed * sign

    @api.multi
    def get_taxes_values(self):
        tax_grouped = {}
        for line in self.invoice_line_ids:
            tot_discount = line.price_unit * ((line.discount or 0.0) / 100.0)
            taxes = line.invoice_line_tax_ids.compute_all(
                line.price_unit, self.currency_id, line.quantity,
                line.product_id, self.partner_id,
                discount=line.discount)['taxes']
            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
                # If the taxes generate moves on the same financial account as
                # the invoice line, propagate the analytic account from the
                # invoice line to the tax line. This is necessary in situations
                # were (part of) the taxes cannot be reclaimed, to ensure the
                # tax move is allocated to the proper analytic account.
                if not val.get('account_analytic_id') and \
                        line.account_analytic_id and \
                        val['account_id'] == line.account_id.id:
                    val['account_analytic_id'] = line.account_analytic_id.id

                key = self.env['account.tax'].browse(
                    tax['id']).get_grouping_key(val)

                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
        return tax_grouped

    def get_document_class_default(self, document_classes):
        if self.turn_issuer.vat_affected not in ['SI', 'ND']:
            exempt_ids = [
                self.env.ref('l10n_cl_invoice.dc_y_f_dtn').id,
                self.env.ref('l10n_cl_invoice.dc_y_f_dte').id]
            for document_class in document_classes:
                if document_class.sii_document_class_id.id in exempt_ids:
                    document_class_id = document_class.id
                    break
                else:
                    document_class_id = document_classes.ids[0]
        else:
            document_class_id = document_classes.ids[0]
        return document_class_id

    @api.onchange('journal_id', 'company_id')
    def _set_available_issuer_turns(self):
        for rec in self:
            if rec.company_id:
                available_turn_ids = rec.company_id.company_activities_ids
                for turn in available_turn_ids:
                    rec.turn_issuer = turn.id

    @api.model
    def name_get(self):
        TYPES = {
            'out_invoice': _('Invoice'),
            'in_invoice': _('Supplier Invoice'),
            'out_refund': _('Refund'),
            'in_refund': _('Supplier Refund'),
        }
        result = []
        for inv in self:
            name = u'{} ({})'.format(
                inv.document_number or TYPES[inv.type], inv.name or '')
            result.append((inv.id, name))
        return result

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100,
                     name_get_uid=None):
        # args = args or []
        args = [] if args is None else args.copy()
        if not (name == '' and operator == 'ilike'):
            recs = self.browse()
            if name:
                recs = self.search(
                    [('document_number', '=', name)] + args, limit=limit)
            if not recs:
                recs = self.search([('name', operator, name)] + args,
                                   limit=limit)
            # return recs.name_get()
        return super(AccountInvoice, self)._name_search(
            name='', args=args, operator='ilike', limit=limit,
            name_get_uid=name_get_uid)

    def _buscar_tax_equivalente(self, tax):
        tax_n = self.env['account.tax'].search(
            [
                ('sii_code', '=', tax.sii_code),
                ('sii_type', '=', tax.sii_type),
                ('retencion', '=', tax.retencion),
                ('type_tax_use', '=', tax.type_tax_use),
                ('no_rec', '=', tax.no_rec),
                ('company_id', '=', self.company_id.id),
                ('price_include', '=', tax.price_include),
                ('amount', '=', tax.amount),
                ('amount_type', '=', tax.amount_type),
            ]
        )
        return tax_n

    def _crearTaxEquivalente(self):
        tax_n = self.env['account.tax'].create({
            'sii_code': tax.sii_code,
            'sii_type': tax.sii_type,
            'retencion': tax.retencion,
            'type_tax_use':tax.type_tax_use,
            'no_rec': tax.no_rec,
            'name': tax.name,
            'description': tax.description,
            'tax_group_id': tax.tax_group_id.id,
            'company_id': self.company_id.id,
            'price_include':tax.price_include,
            'amount': tax.amount,
            'amount_type': tax.amount_type,
            'account_id':tax.account_id.id,
            'refund_account_id': tax.refund_account_id.id,
        })
        return tax

    @api.onchange('company_id')
    def _refresh_records(self):
        if self.journal_id and self.journal_id.company_id != self.company_id.id:
            inv_type = self._context.get('type', 'out_invoice')
            inv_types = inv_type if isinstance(inv_type, list) else [inv_type]
            company_id = self._context.get('company_id', self.company_id.id)
            domain = [
                ('type', 'in', filter(None, map(TYPE2JOURNAL.get, inv_types))),
                ('company_id', '=', company_id),
            ]
            journal = self.journal_id = self.env['account.journal'].search(
                domain, limit=1)
            for line in self.invoice_line_ids:
                tax_ids = []
                if self._context.get('type') in ('out_invoice', 'in_refund'):
                    line.account_id = journal.default_credit_account_id.id
                else:
                    line.account_id = journal.default_debit_account_id.id
                if self._context.get('type') in ('out_invoice', 'out_refund'):
                    for tax in line.product_id.taxes_id:
                        if tax.company_id.id == self.company_id.id:
                            tax_ids.append(tax.id)
                        else:
                            tax_n = self._buscar_tax_equivalente(tax)
                            if not tax_n:
                                tax_n = self._crearTaxEquivalente(tax)
                            tax_ids.append(tax_n.id)
                    line.product_id.taxes_id = False
                    line.product_id.taxes_id = tax_ids
                else:
                    for tax in line.product_id.supplier_taxes_id:
                        if tax.company_id.id == self.company_id.id:
                            tax_ids.append(tax.id)
                        else:
                            tax_n = self._buscar_tax_equivalente(tax)
                            if not tax_n:
                                tax_n = self._crearTaxEquivalente(tax)
                            tax_ids.append(tax_n.id)
                    line.invoice_line_tax_ids = False
                    line.product_id.supplier_taxes_id.append = tax_ids
                line.invoice_line_tax_ids = False
                line.invoice_line_tax_ids = tax_ids

    @api.one
    @api.depends('journal_id', 'partner_id', 'turn_issuer')
    def _get_available_journal_document_class(self):
        invoice_type = self.type
        document_class_ids = []
        document_class_id = False
        self.available_journal_document_class_ids = self.env[
            'account.journal.sii_document_class']
        if invoice_type in [
                'out_invoice', 'in_invoice', 'out_refund', 'in_refund']:
            operation_type = self.get_operation_type(invoice_type)
            if self.use_documents:
                letter_ids = self.get_valid_document_letters(
                    self.partner_id.id, operation_type, self.company_id.id)
                # domain = [
                #     ('journal_id', '=', self.journal_id.id),
                #     '|', ('sii_document_class_id.document_letter_id',
                #           'in', letter_ids),
                #          ('sii_document_class_id.document_letter_id',
                #           '=', False)]
                # If document_type in context we try to serch specific document
                # domain modificado
                document_type = self._context.get('document_type', False)
                if document_type:
                    document_classes = self.env[
                        'account.journal.sii_document_class'].search(
                        domain + [('sii_document_class_id.document_type',
                                   '=', document_type)])
                    if document_classes.ids:
                        # revisar si hay condicion de exento, para poner como
                        # primera alternativa estos
                        document_class_id = self.get_document_class_default(
                            document_classes)
                # For domain, we search all documents
                #### linea de reemplazo de todo el resto
                domain = [('journal_id', '=', self.journal_id.id),]
                #####
                # raise UserError(json.dumps(domain))
                document_classes = self.env[
                    'account.journal.sii_document_class'].search(domain)
                document_class_ids = document_classes.ids
                # If not specific document type found, we choose another one
                if not document_class_id and document_class_ids:
                    # revisar si hay condicion de exento, para poner
                    # como primera alternativa estos
                    # todo: manejar más fino el documento por defecto.
                    document_class_id = self.get_document_class_default(
                        document_classes)
        self.available_journal_document_class_ids = document_class_ids
        self.journal_document_class_id = document_class_id

    @api.onchange('journal_document_class_id')
    def _select_fiscal_position(self):
        exempt_ids = [
            self.env.ref('l10n_cl_invoice.dc_y_f_dtn').id,
            self.env.ref('l10n_cl_invoice.dc_y_f_dte').id,
            self.env.ref('l10n_cl_invoice.dc_b_e_dtn').id,
            self.env.ref('l10n_cl_invoice.dc_b_e_dte').id]
        if self.journal_document_class_id.sii_document_class_id.id in \
                exempt_ids:
            self.fiscal_position_id = self.env.ref(
                'l10n_cl_invoice.exempt_fp')

    @api.onchange('sii_document_class_id')
    def _check_vat(self):
        boleta_ids = [
            self.env.ref('l10n_cl_invoice.dc_bzf_f_dtn').id,
            self.env.ref('l10n_cl_invoice.dc_b_f_dtm').id]
        if self.sii_document_class_id not in boleta_ids and \
                        self.partner_id.document_number == '' or \
                        self.partner_id.document_number == '0':
            raise UserError(_("""The customer/supplier does not have a VAT \
defined. The type of invoicing document you selected requires you tu settle \
a VAT."""))

    @api.one
    @api.depends(
        'sii_document_class_id',
        'sii_document_class_id.document_letter_id',
        'sii_document_class_id.document_letter_id.vat_discriminated',
        'company_id',
        'company_id.invoice_vat_discrimination_default',)
    def get_vat_discriminated(self):
        vat_discriminated = False
        if self.sii_document_class_id.document_letter_id.vat_discriminated or \
            self.company_id.invoice_vat_discrimination_default == \
                'discriminate_default':
            vat_discriminated = True
        self.vat_discriminated = vat_discriminated

    @api.one
    @api.depends('sii_document_number', 'number')
    def _get_document_number(self):
        if self.sii_document_number and self.sii_document_class_id:
            document_number = \
                (self.sii_document_class_id.doc_code_prefix or '') + \
                self.sii_document_number
        else:
            document_number = self.number
        self.document_number = document_number

    supplier_invoice_number = fields.Char(
        copy=False)
    turn_issuer = fields.Many2one(
        'partner.activities',
        'Giro Emisor', readonly=True, store=True, required=False,
        states={'draft': [('readonly', False)]}, )
    vat_discriminated = fields.Boolean(
        'Discriminate VAT?',
        compute="get_vat_discriminated",
        store=True,
        readonly=False,
        help="Discriminate VAT on Quotations and Sale Orders?")
    available_journals = fields.Many2one(
        'account.journal',
        compute='_get_available_journal_document_class',
        string='Available Journals')
    available_journal_document_class_ids = fields.Many2many(
        'account.journal.sii_document_class',
        compute='_get_available_journal_document_class',
        string='Available Journal Document Classes')
    journal_document_class_id = fields.Many2one(
        'account.journal.sii_document_class',
        'Documents Type',
        default=_get_available_journal_document_class,
        readonly=True,
        store=True,
        states={'draft': [('readonly', False)]})
    sii_document_class_id = fields.Many2one(
        'sii.document_class',
        related='journal_document_class_id.sii_document_class_id',
        string='Document Type',
        copy=False,
        readonly=True,
        store=True)
    sii_document_number = fields.Char(
        string='Document Number',
        copy=False,
        readonly=True,)
    responsability_id = fields.Many2one(
        'sii.responsability',
        string='Responsability',
        related='commercial_partner_id.responsability_id',
        store=True, )
    formated_vat = fields.Char(
        string='Responsability',
        related='commercial_partner_id.formated_vat')
    iva_uso_comun = fields.Boolean(
        string="Uso Común", readonly=True,
        states={'draft': [('readonly', False)], })
    # solamente para compras tratamiento del iva
    no_rec_code = fields.Selection([
        ('1', 'Compras destinadas a IVA a generar operaciones no gravados \
o exentas.'),
        ('2', 'Facturas de proveedores registrados fuera de plazo.'),
        ('3', 'Gastos rechazados.'), ('4', 'Entregas gratuitas (premios, \
bonificaciones, etc.) recibidos.'), ('9', 'Otros.')], string="Código No \
recuperable", readonly=True, states={'draft': [('readonly', False)]})
    document_number = fields.Char(
        compute='_get_document_number',
        string='Document Number',
        readonly=True, )
    next_invoice_number = fields.Integer(
        related='journal_document_class_id.sequence_id.number_next_actual',
        string='Next Document Number',
        readonly=True)
    use_documents = fields.Boolean(
        related='journal_id.use_documents',
        string='Use Documents?',
        readonly=True)
    referencias = fields.One2many(
        'account.invoice.referencias', 'invoice_id', readonly=True,
        states={'draft': [('readonly', False)]})
    forma_pago = fields.Selection([('1', 'Contado'), ('2', 'Crédito'), ('3', '\
Gratuito')], string="Forma de pago", readonly=True, states={'draft': [('\
readonly', False)]}, default='1')
    contact_id = fields.Many2one('res.partner', string="Contacto")

    @api.one
    @api.constrains('supplier_invoice_number', 'partner_id', 'company_id')
    def _check_reference(self):
        if self.type in ['out_invoice', 'out_refund'] and self.reference and \
                        self.state == 'open':
            domain = [('type', 'in', ('out_invoice', 'out_refund')),
                      # ('reference', '=', self.reference),
                      ('document_number', '=', self.document_number),
                      ('journal_document_class_id.sii_document_class_id', '=',
                       self.journal_document_class_id.sii_document_class_id.id),
                      ('company_id', '=', self.company_id.id),
                      ('id', '!=', self.id)]
            invoice_ids = self.search(domain)
            if invoice_ids:
                raise UserError(
                    _('Supplier Invoice Number must be unique per Supplier and \
Company!'))

    _sql_constraints = [('number_supplier_invoice_number',
                         'unique(supplier_invoice_number, partner_id, \
company_id)', 'Supplier Invoice No must be unique per Supplier and Company!')]

    @api.multi
    def action_move_create(self):
        for obj_inv in self:
            invtype = obj_inv.type
            if obj_inv.journal_document_class_id and not \
                    obj_inv.sii_document_number:
                if invtype in ('out_invoice', 'out_refund'):
                    if not obj_inv.journal_document_class_id.sequence_id:
                        raise osv.except_osv(_('Error!'), _('Please define \
sequence on the journal related documents to this invoice.'))
                    sii_document_number = obj_inv.journal_document_class_id.\
                        sequence_id.next_by_id()
                    prefix = obj_inv.journal_document_class_id.\
                                 sii_document_class_id.doc_code_prefix or ''
                    move_name = (
                        prefix + str(sii_document_number)).replace(' ', '')
                    obj_inv.write({'move_name': move_name})
                elif invtype in ('in_invoice', 'in_refund'):
                    sii_document_number = \
                        obj_inv.supplier_invoice_number.zfill(6)
        super(AccountInvoice, self).action_move_create()
        for obj_inv in self:
            invtype = obj_inv.type
            if obj_inv.journal_document_class_id and not \
                    obj_inv.sii_document_number:
                obj_inv.write({'sii_document_number': sii_document_number})
            document_class_id = obj_inv.sii_document_class_id.id
            guardar = {
                'document_class_id': document_class_id,
                'sii_document_number': obj_inv.sii_document_number,
                'no_rec_code': obj_inv.no_rec_code,
                'iva_uso_comun': obj_inv.iva_uso_comun}
            obj_inv.move_id.write(guardar)
        return True

    def get_operation_type(self, invoice_type):
        if invoice_type in ['in_invoice', 'in_refund']:
            operation_type = 'purchase'
        elif invoice_type in ['out_invoice', 'out_refund']:
            operation_type = 'sale'
        else:
            operation_type = False
        return operation_type

    def get_valid_document_letters(
            self, partner_id, operation_type='sale',
            company=False, vat_affected='SI', invoice_type='out_invoice'):

        document_letter_obj = self.env['sii.document_letter']
        user = self.env.user
        partner = self.partner_id
        if not company:
            company = self.company_id
        if not partner_id or not company or not operation_type:
            return []
        partner = partner.commercial_partner_id

        if operation_type == 'sale':
            issuer_responsability_id = self.company_id.partner_id.\
                responsability_id.id
            receptor_responsability_id = partner.responsability_id.id
            if invoice_type == 'out_invoice':
                if vat_affected == 'SI':
                    domain = [
                        ('issuer_ids', '=', issuer_responsability_id),
                        ('receptor_ids', '=', receptor_responsability_id),
                        ('name', '!=', 'C')]
                else:
                    domain = [
                        ('issuer_ids', '=', issuer_responsability_id),
                        ('receptor_ids', '=', receptor_responsability_id),
                        ('name', '=', 'C')]
            else:
                # nota de credito de ventas
                domain = [
                    ('issuer_ids', '=', issuer_responsability_id),
                    ('receptor_ids', '=', receptor_responsability_id)]
        elif operation_type == 'purchase':
            issuer_responsability_id = partner.responsability_id.id
            receptor_responsability_id = self.company_id.partner_id.\
                responsability_id.id
            if invoice_type == 'in_invoice':
                _logger.info('responsabilidad del partner')
                if issuer_responsability_id == self.env['ir.model.data'].\
                        get_object_reference('l10n_cl_invoice', 'res_BH')[1]:
                    _logger.info('el proveedor es de segunda categoria y emite \
boleta de honorarios')
                else:
                    _logger.info('el proveedor es de primera categoria y emite \
facturas o facturas no afectas')
                domain = [
                    ('issuer_ids', '=', issuer_responsability_id),
                    ('receptor_ids', '=', receptor_responsability_id)]
            else:
                # nota de credito de compras
                domain = [
                    '|',
                    ('issuer_ids', '=', issuer_responsability_id),
                    ('receptor_ids', '=', receptor_responsability_id)]
        else:
            raise except_orm(_('Operation Type Error'),
                             _('Operation Type Must be "Sale" or "Purchase"'))

        # TODO: fijar esto en el wizard, o llamar un wizard desde aca
        # if not company.partner_id.responsability_id.id:
        #     raise except_orm(_('You have not settled a tax payer type for
        #  your\
        #      company.'),
        #      _('Please, set your company tax payer type (in company or \
        #      partner before to continue.'))

        document_letter_ids = document_letter_obj.search(domain)
        return document_letter_ids

    @api.multi
    def invoice_validate(self):
        for invoice in self:
            # refuse to validate a vendor bill/refund if there already exists
            # one with the same reference for the same partner,
            # because it's probably a double encoding of the same bill/refund
            if invoice.type in ('in_invoice', 'in_refund') and \
                    invoice.reference:
                if self.search([('reference', '=', invoice.reference),
                                ('journal_document_class_id', '=',
                                 invoice.journal_document_class_id.id),
                                ('partner_id', '=', invoice.partner_id.id),
                                ('type', '=', invoice.type),
                                ('id', '!=', invoice.id)]):
                    raise UserError(
                        'Doc %s Folio %s de %s ya se registro' % (
                            invoice.journal_document_class_id.
                            sii_document_class_id.name,
                            invoice.reference, invoice.partner_id.name))
        return self.write({'state': 'open'})


class Referencias(models.Model):
    _name = 'account.invoice.referencias'

    origen = fields.Char(string="Origin")
    sii_referencia_TpoDocRef = fields.Many2one('sii.document_class', string="\
SII Reference Document Type")
    sii_referencia_CodRef = fields.Selection(
        [('1', 'Anula Documento de Referencia'),
         ('2', 'Corrige texto Documento Referencia'),
         ('3', 'Corrige montos')], string="SII Reference Code")
    motivo = fields.Char(string="Motivo")
    invoice_id = fields.Many2one(
        'account.invoice', ondelete='cascade', index=True, copy=False,
        string="Documento")
    fecha_documento = fields.Date(string="Fecha Documento", required=True)
