# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import Warning

class SIISucursal(models.Model):
    _name = 'sii.sucursal'

    name = fields.Char(string='Nombre de la Sucursal', required=True)
    sii_code = fields.Char(string="Código SII de la Sucursal", )
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda self: self.env.user.company_id.id, )

class sii_point_of_sale(models.Model):
    _name = 'sii.point_of_sale'
    _description = 'SII Point Of Sale'

    @api.one
    @api.depends('number')
    def _get_code(self):
        code = False
        if self.number:
            # TODO rellenar el number a cuatro
            code = str(self.number)
        self.code = code
    name = fields.Char(
        'Name', required=True)
    number = fields.Integer(
        'Number', required=True)
    code = fields.Char(
        'Code', compute="_get_code")
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda self: self.env.user.company_id.id,
        )

    _sql_constraints = [('number_unique', 'unique(number, company_id)',
                         'Number Must be Unique per Company!'), ]


class sii_document_class(models.Model):
    _name = 'sii.document_class'
    _description = 'SII Document Class'

    name = fields.Char(
        'Name', size=120)
    doc_code_prefix = fields.Char(
        'Document Code Prefix', help="Prefix for Documents Codes on Invoices \
and Account Moves. For eg. 'FAC' will build 'FAC 00001' Document Number")
    code_template = fields.Char(
        'Code Template for Journal')
    sii_code = fields.Integer(
        'SII Code', required=True)
    document_letter_id = fields.Many2one(
        'sii.document_letter', 'Document Letter')
    report_name = fields.Char(
        'Name on Reports',
        help='Name that will be printed in reports, for example "CREDIT NOTE"')
    document_type = fields.Selection(
        [
            ('invoice', 'Invoices'),
            ('invoice_in', 'Purchase Invoices'),
            ('debit_note', 'Debit Notes'),
            ('credit_note', 'Credit Notes'),
            ('stock_picking', 'Stock Picking'),
            ('other_document', 'Other Documents')
        ],
        string='Document Type',
        help='It defines some behaviours on automatic journal selection and \
in menus where it is shown.')
    active = fields.Boolean(
        'Active', default=True)
    dte = fields.Boolean(
        'DTE', required=True)


class sii_document_letter(models.Model):
    _name = 'sii.document_letter'
    _description = 'Sii Document letter'

    name = fields.Char(
        'Name', size=64, required=True)
    sii_document_class_ids = fields.One2many(
        'sii.document_class', 'document_letter_id', 'SII Document Classes')
    issuer_ids = fields.Many2many(
        'sii.responsability', 'sii_doc_letter_issuer_rel',
        'letter_id', 'responsability_id', 'Issuers',)
    receptor_ids = fields.Many2many(
        'sii.responsability', 'sii_doc_letter_receptor_rel',
        'letter_id', 'responsability_id', 'Receptors',)
    active = fields.Boolean(
        'Active', default=True)
    vat_discriminated = fields.Boolean(
        'Vat Discriminated on Invoices?',
        help="If True, the vat will be discriminated on invoice report.")

    _sql_constraints = [('name', 'unique(name)', 'Name must be unique!'), ]


class sii_responsability(models.Model):
    _name = 'sii.responsability'
    _description = 'SII VAT Responsability'

    name = fields.Char(
        'Name', size=64, required=True)
    code = fields.Char(
        'Code', size=8, required=True)
    tp_sii_code = fields.Integer('Tax Payer SII Code', required=True)
    active = fields.Boolean(
        'Active', default=True)
    issued_letter_ids = fields.Many2many(
        'sii.document_letter', 'sii_doc_letter_issuer_rel',
        'responsability_id', 'letter_id', 'Issued Document Letters')
    received_letter_ids = fields.Many2many(
        'sii.document_letter', 'sii_doc_letter_receptor_rel',
        'responsability_id', 'letter_id', 'Received Document Letters')

    _sql_constraints = [('name', 'unique(name)', 'Name must be unique!'),
                        ('code', 'unique(code)', 'Code must be unique!')]


class sii_document_type(models.Model):
    _name = 'sii.document_type'
    _description = 'SII document types'

    name = fields.Char(
        'Name', size=120, required=True)
    code = fields.Char(
        'Code', size=16, required=True)
    sii_code = fields.Integer(
        'SII Code', required=True)
    active = fields.Boolean(
        'Active', default=True)


class sii_concept_type(models.Model):
    _name = 'sii.concept_type'
    _description = 'SII concept types'

    name = fields.Char(
        'Name', size=120, required=True)
    sii_code = fields.Integer(
        'SII Code', required=True)
    active = fields.Boolean(
        'Active', default=True)
    product_types = fields.Char(
        'Product types',
        help='Translate this product types to this SII concept.\
        Types must be a subset of adjust,\
        consu and service separated by commas.',
        required=True)

    @api.one
    @api.constrains('product_types')
    def _check_product_types(self):
        if self.product_types:
            types = set(self.product_types.split(','))
            if not types.issubset(['adjust', 'consu', 'service']):
                raise Warning(_('You provided an invalid list of product types.\
                Must been separated by commas'))


class sii_optional_type(models.Model):
    _name = 'sii.optional_type'
    _description = 'SII optional types'

    name = fields.Char(
        'Name', size=120, required=True)
    sii_code = fields.Integer(
        'SII Code', required=True)
    apply_rule = fields.Char(
        'Apply rule')
    value_computation = fields.Char(
        'Value computation')
    active = fields.Boolean(
        'Active', default=True)
