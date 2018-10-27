# -*- coding: utf-8 -*-
# Part of Konos. See LICENSE file for full copyright and licensing details.

import tempfile
import binascii
import logging
from datetime import datetime
from odoo.exceptions import Warning
from odoo import models, fields, api, exceptions, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

_logger = logging.getLogger(__name__)
try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')



try:
    import xlrd
except ImportError:
    _logger.debug('Cannot `import xlrd`.')


class account_bank_statement_wizard(models.TransientModel):
    _name= "account.bank.statement.wizard"

    file = fields.Binary('File')
    file_opt = fields.Selection([('excel','Excel'),('csv','CSV')], default='excel')
    bank_opt = fields.Selection([('santander','Santander'),('estado','Banco Estado'),('chile','Banco de Chile'),('itau','Banco Itau')])


    @api.multi
    def import_file(self):
        #if not file:
        #    raise Warning('Please Select File')
        if self.file_opt == 'csv':
            keys = ['date','ref','partner','memo','amount']                    
            data = base64.b64decode(self.file)
            file_input = io.StringIO(data.decode("utf-8"))
            file_input.seek(0)
            reader_info = []
            reader = csv.reader(file_input, delimiter=',')
 
            try:
                reader_info.extend(reader)
            except Exception:
                raise exceptions.Warning(_("Not a valid file!"))
            values = {}
            for i in range(len(reader_info)):
                field = list(map(str, reader_info[i]))
                values = dict(zip(keys, field))
                if values:
                    if i == 0:
                        continue
                    else:
                        res = self._create_statement_lines(values)
        elif self.file_opt == 'excel':
            fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.file))
            fp.seek(0)
            values = {}
            workbook = xlrd.open_workbook(fp.name)
            sheet = workbook.sheet_by_index(0)
            contador = 0
            if self.bank_opt == 'santander':
                for row_no in range(sheet.nrows):
                    line = list(map(lambda row:isinstance(row.value, str) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                    try:
                        fecha=line[3].decode("utf-8")
                        date_string = datetime.strptime(fecha, '%d/%m/%Y').strftime('%Y-%m-%d')
                        values.update( {'date':date_string,
                                        'ref': '',
                                        'partner': line[7],
                                        'memo': line[1].decode("utf-8"),
                                        'amount': line[0],
                                       })
                        res = self._create_statement_lines(values)
                    except:
                        _logger.warning('No encuentra Fecha')
            elif self.bank_opt == 'chile':
                for row_no in range(sheet.nrows):
                    if row_no <= 1:
                        fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
                    else:
                        line = list(map(lambda row:isinstance(row.value, str) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                        data = line[0].decode("utf-8").split(",")
                        fecha=data[0]
                        date_string = datetime.strptime(fecha, '%d/%m/%Y').strftime('%Y-%m-%d')
                        if data[3]=='0': 
                            values.update( {'date':date_string,
                                            'ref': data[1],
                                            'partner': 'X',
                                            'memo': data[1],
                                            'amount': int(data[2])* (-1),
                                           })
                        else: 
                            values.update( {'date':date_string,
                                            'ref': data[1],
                                            'partner': 'X',
                                            'memo': data[1],
                                            'amount': data[3],
                                           })
                        res = self._create_statement_lines(values)
            elif self.bank_opt == 'estado':
                for row_no in range(sheet.nrows):

                    if row_no <= 0:
                        fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
                    else:
                        line = list(map(lambda row:isinstance(row.value, str) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))


                        date_string = line[5]
                        date_string = date_string[:10]
                        try:
                            date_string = datetime.strptime(date_string, '%d/%m/%Y').strftime('%Y-%m-%d')
                        except:
                            date_string = '01-01-01'
                            contador = contador + 1
                        if date_string != '01-01-01' and contador <=100:
                            contador = 100
                            #if line[3] in (None, "", 0, '0'):
                            if line[3] <= line[4] or (line[3] in (None, "", 0, '0', "0")): 
                                values.update( {'date':date_string,
                                                'ref': line[0].decode("utf-8"),
                                                'partner': line[6],
                                                'memo': line[1].decode("utf-8"),
                                                'amount': int(line[4].replace('.', '')) / 10,
                                               })
                            else:
                                values.update( {'date':date_string,
                                                'ref': line[0].decode("utf-8"),
                                                'partner': line[6],
                                                'memo': line[1].decode("utf-8"),
                                                #'amount': line[3] * (-1),
                                                'amount': int(line[3].replace('.', '')) * (-1) / 10,
                                               })
                            res = self._create_statement_lines(values)  
            else:
                #ITAU Este es el fin y se recorre invertido
                ano=sheet.cell(11,3).value
                ano=ano[-5:]
                for row_no in range(sheet.nrows-11):
                    if row_no > 26:
                        line = list(map(lambda row:isinstance(row.value, str) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                        date_string = str(line[0]).replace("'", "").replace('b', '')+ano
                        date_string = datetime.strptime(date_string, '%d/%m/%Y').strftime('%Y-%m-%d')
                        
                        if line[4] <= line[5]: 
                            values.update( {'date':date_string,
                                        'ref': line[1],
                                        'partner': line[6],
                                        'memo': line[3].decode("utf-8"),
                                        'amount': int(line[5].replace('.0', ''))*(-1),
                                        })
                        else:
                            values.update( {'date':date_string,
                                        'ref': line[1],
                                        'partner': line[6],
                                        'memo': line[3].decode("utf-8"),
                                        'amount': line[4],
                                        })
                        res = self._create_statement_lines(values)        

                    
        else:
            raise Warning('Please Select File Type')
        self.env['account.bank.statement'].browse(self._context.get('active_id'))._end_balance()
        return res
#
    @api.multi
    def _create_statement_lines(self,val):
        partner_id = self._find_partner(val.get('partner'))
        if not val.get('date'):
            raise Warning('Please Provide Date Field Value')
        if not val.get('memo'):
            raise Warning('Please Provide Memo Field Value')
        aaa = self._cr.execute("insert into account_bank_statement_line (date,ref,partner_id,name,amount,statement_id) values (%s,%s,%s,%s,%s,%s)",(val.get('date'),val.get('ref'), partner_id,val.get('memo'),val.get('amount'),self._context.get('active_id')))
        return True
#
    def _find_partner(self,name):
        partner_id = self.env['res.partner'].search([('name','=',name)])
        if partner_id:
            return partner_id.id
        else:
            return



