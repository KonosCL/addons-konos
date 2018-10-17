# -*- coding: utf-8 -*-
##############################################################################
#
#    Konos
#    Copyright (C) 2018 Konos (<http://konos.cl/>)
#
##############################################################################

from odoo.tools.misc import str2bool, xlwt
from xlsxwriter.workbook import Workbook
import base64
import re,sys
import io
from odoo import api, fields, models
from xlwt import easyxf
import csv
import time
from datetime import datetime, date

import logging
_logger = logging.getLogger(__name__)



class bank_statement_excel_wizard_form(models.TransientModel):
    _name ='bank.statement.excel.wizard'




    
    def bank_statement_history_excel(self):
        bank_statement_line_ids = self._context.get('active_ids')
        bank_statement_obj = self.env['account.bank.statement']


        i = 0
        sheetName = 1
        workbook = xlwt.Workbook()
        worksheet=[]
        for l in range(0,len(bank_statement_line_ids)):
            worksheet.append(l)

        
        for bank_statement in bank_statement_obj.browse(bank_statement_line_ids):
            n = 9
            c = 1
            style1 = xlwt.easyxf('pattern: pattern solid, fore_colour gray25;''font:bold True')
            filename = 'bank_statement_report.xls'
            style = xlwt.XFStyle()
            tall_style = xlwt.easyxf('font:height 720;') # 36pt
            font = xlwt.Font()
            font.name = 'Times New Roman'
            font.bold = True
            font.height = 250
            currency = xlwt.easyxf('font: height 180; align: wrap yes, horiz right',num_format_str='#,##0.00') 


            if bank_statement.name:
                worksheet[i] = workbook.add_sheet(str(bank_statement.name))
            else:
                worksheet[i] = workbook.add_sheet(str(sheetName))
                sheetName += 1

            
            formato_fecha=xlwt.easyxf(num_format_str='DD-MM-YY')
            worksheet[i].write_merge(0, 0, 1, 3, "ANALISIS DE CUENTAS", style)

            worksheet[i].col(0).width = 1000
            worksheet[i].col(1).width = 5000
            worksheet[i].col(2).width = 6500
            worksheet[i].col(3).width = 6500
            worksheet[i].col(4).width = 4500
            worksheet[i].col(5).width = 4000
            worksheet[i].col(6).width = 4000




            fecha = datetime.strptime(bank_statement.date,'%Y-%m-%d')
            ano = fecha.year
            mes = fecha.strftime('%m')

            worksheet[i].write(1, 1, 'Fecha', style1)
            worksheet[i].write(1, 2, bank_statement.date or '',formato_fecha)
            worksheet[i].write(2, 1, 'Cuenta', style1)
            worksheet[i].write(2, 2, bank_statement.journal_id.default_credit_account_id.code + ' ' + bank_statement.journal_id.default_credit_account_id.name or '')
            worksheet[i].write(3, 1, 'Descripción:', style1)
            worksheet[i].write(3, 2, bank_statement.journal_id.name, style)
            worksheet[i].write(4, 1, 'Mes:', style1)
            worksheet[i].write(4, 2, fecha.month, style)
            worksheet[i].write(5, 1, 'Año:', style1)
            worksheet[i].write(5, 2, ano, style)
            

            worksheet[i].write(8,1, 'Fecha', style1)
            worksheet[i].write(8,2, 'Referencia', style1)
            worksheet[i].write(8,3, 'Glosa Comprobante', style1)
            worksheet[i].write(8,4, 'Nº Doc', style1)
            worksheet[i].write(8,5, 'Monto', style1)
            worksheet[i].write(8,6, 'Mayor', style1)
            worksheet[i].write(9,6, bank_statement.balance_end_real ,currency)

           # query = """SELECT * FROM account_move_line where (to_char(date_maturity,'mm')= %s) and (to_char(date_maturity,'yyyy')= '%s') and account_id = %s and statement_id != %s""",(mes, ano,bank_statement.journal_id.default_credit_account_id.id,bank_statement.id)
			#_logger.warning(query)

  #          self.env.cr.execute("""SELECT * FROM account_move_line where 
 #(to_char(date,'mm')= %s)
#and (to_char(date,'yyyy')= '%s') and account_id = %s and (statement_id is null or statement_id != %s)""",(mes, ano,bank_statement.journal_id.default_credit_account_id.id,bank_statement.id))
            
            self.env.cr.execute("""SELECT * FROM account_move_line where (date<= %s) and account_id = %s and statement_id is null order by date""",(bank_statement.date,bank_statement.journal_id.default_credit_account_id.id))
           

                
            line_list = [o for o in self.env.cr.dictfetchall()]

            suma = 0                    
            for rec in line_list:
                worksheet[i].write(n, c, rec['date'], formato_fecha)
                worksheet[i].write(n, c+1, rec['name'], style)
                worksheet[i].write(n, c+2, rec['ref'], style)
                worksheet[i].write(n, c+3, rec['document_number'], style)
                worksheet[i].write(n, c+4, rec['balance'],currency)
                suma = suma + float(rec['balance'])
                n = n+1

            worksheet[i].write(n+1,2, 'Saldo Según Cartola', style)
            worksheet[i].write(n+1,6, suma + bank_statement.balance_end_real,currency)
                

                


  



            

        
        fp = io.BytesIO()
        workbook.save(fp)
            
        
        export_id = self.env['bank.statement.excel'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        fp.close()
        
        return {
            'view_mode': 'form',
            'res_id': export_id.id,
            'res_model': 'bank.statement.excel',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'context': self._context,
            'target': 'new',
            
        }
        return True


class bank_statement_excel(models.TransientModel):
    _name= "bank.statement.excel"
    excel_file = fields.Binary('Excel Report for Transit Accounts')
    file_name = fields.Char('Excel File', size=64)



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
