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



class account_move_excel_wizard_form(models.TransientModel):
    _name ='wizard.export.account.centralized'

    date_to = fields.Date('Fecha Final', required=True)
    libro_id = fields.Many2one('account.journal', 'Salary Journal')


    _defaults = {
        'date_to': lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],

    }


    
    def account_centralized_history_excel(self):
        date_stop = self.date_to
        libro = self.libro_id.id

        fecha = datetime.strptime(date_stop,'%Y-%m-%d')
        ano = fecha.year
        mes = fecha.strftime('%m')
        account_move_line_ids = self.env['account.move.line'].search([('date','=',date_stop)])


        i = 1
        sheetName = 1
        workbook = xlwt.Workbook()
        
        n = 5
        c = 1
        style1 = xlwt.easyxf('pattern: pattern solid, fore_colour gray25;''font:bold True')
        filename = 'account_move_report.xls'
        style = xlwt.XFStyle()
        tall_style = xlwt.easyxf('font:height 720;') # 36pt
        font = xlwt.Font()
        font.name = 'Times New Roman'
        font.bold = True
        font.height = 250
        currency = xlwt.easyxf('font: height 180; align: wrap yes, horiz right',num_format_str='#,##0.00') 
        formato_fecha=xlwt.easyxf(num_format_str='DD-MM-YY')
        worksheet = workbook.add_sheet("CENTRALIZACION"+str(mes)+str(ano))
        

        worksheet.write_merge(0, 0, 2, 5, "CENTRALIZACION DE REMUNERACIONES", style)
        worksheet.write(1, 2, 'Mes', style)
        worksheet.write(1, 3, mes, style)
        worksheet.write(2, 2, 'Año', style)
        worksheet.write(2, 3, str(ano), style)

        comprobantes = ""
        self.env.cr.execute("""SELECT name  FROM account_move where (to_char(date,'mm')= %s) and (to_char(date,'yyyy')= '%s') and journal_id='%s' GROUP BY name """,(mes,ano,libro))
        listado = [o for o in self.env.cr.dictfetchall()]               
        for nombres in listado:
            comprobantes= comprobantes + nombres['name'] + str(", ")








        self.env.cr.execute("""SELECT sum(balance) as suma,  code,  account_account.name as nombre  FROM account_move_line left join account_account
on  account_account.id = account_move_line.account_id  where (to_char(date,'mm')= %s) and (to_char(date,'yyyy')= '%s') and journal_id='%s' GROUP BY code,  account_account.name """,(mes,ano,libro))

        worksheet.col(0).width = 500
        worksheet.col(1).width = 500
        worksheet.col(2).width = 3000
        worksheet.col(3).width = 7000
        worksheet.col(4).width = 3000
        worksheet.col(5).width = 3000
     
        worksheet.write_merge(n-1, n-1, 2, 3, 'Cuenta', style1)
        worksheet.write(n-1, 4, 'Debe', style1)
        worksheet.write(n-1, 5, 'Haber', style1)


        line_list = [o for o in self.env.cr.dictfetchall()]

        debe = 0
        haber = 0                
        for rec in line_list:
            
            worksheet.write(n, c+1, rec['code'], style)
            worksheet.write(n, c+2, rec['nombre'], style)

            if rec['suma'] > 0:
                worksheet.write(n, c+3, rec['suma'], currency)            
                debe = debe + float(rec['suma'])
            else:
                worksheet.write(n, c+4, float(rec['suma']) * -1, currency)       
                haber = haber + (float(rec['suma']) * -1)
            n = n+1


        worksheet.write(n,4, debe, currency)
        worksheet.write(n,5, haber, currency)

        worksheet.write(n+3,2, "Comprobantes:", style)
        worksheet.write(n+3,3, comprobantes, style)




        fp = io.BytesIO()
        workbook.save(fp)
            
        
        export_id = self.env['account.centralized.excel'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        fp.close()
        
        return {
            'view_mode': 'form',
            'res_id': export_id.id,
            'res_model': 'account.centralized.excel',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'context': self._context,
            'target': 'new',
            
        }
        return True


class account_centralized_excel(models.TransientModel):
    _name= "account.centralized.excel"
    excel_file = fields.Binary('Excel Report for Centralized Accounts')
    file_name = fields.Char('Excel File', size=64)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
