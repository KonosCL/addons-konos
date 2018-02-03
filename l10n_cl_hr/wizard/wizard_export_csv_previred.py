# -*- encoding: utf-8 -*-
########################################################################
#
# @authors: Carlos Lopez Mite(celm1990@hotmail.com), - Nelson Ramírez Sánchez (info@nelsonramirez.com)
#    
#    
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import io
import csv
import base64
from datetime import datetime
import logging
from odoo import models, api, fields
import time
import odoo.addons.decimal_precision as dp
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from dateutil import relativedelta

class WizardExportCsvPrevired(models.TransientModel):

    _name = 'wizard.export.csv.previred'
    _description = 'wizard.export.csv.previred'
    
    delimiter = ";"
    quotechar = '"'
    date_from = fields.Date('Fecha Inicial', required=True)
    date_to = fields.Date('Fecha Final', required=True)
    file_data = fields.Binary('Archivo csv', filters=None, help="",)
    file_name = fields.Char('Nombre de archivo', size=256, required=False, help="",)

    _defaults = {
        'date_from': lambda *a: time.strftime('%Y-%m-01'),
        'date_to': lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],

    }

    def show_view(self, cr, uid, name, model, id_xml, res_id=None, view_mode='tree,form', nodestroy=True, target='new', context=None):
        if not context:
            context = {}
        mod_obj = self.pool.get('ir.model.data')
        view_obj = self.pool.get('ir.ui.view')
        module = ""
        if "." in id_xml:
            module, id_xml = id_xml.split(".", 1)
        res = mod_obj.get_object_reference(cr, uid, module, id_xml)
        view_id = res and res[1] or False
        if view_id:
            view = view_obj.browse(cr, uid, view_id, context)
            view_mode = view.type
        ctx = context.copy()
        ctx.update({'active_model': model})
        res = {'name': name,
                'view_type': 'form',
                'view_mode': view_mode,
                'view_id': view_id,
                'res_model': model,
                'res_id': res_id,
                'nodestroy': nodestroy,
                'target': target,
                'type': 'ir.actions.act_window',
                'context': ctx,
                }
        return res    
    
    @api.model
    def get_nacionalidad(self, employee):
        #0 chileno, 1 extranjero, comparar con el pais de la compañia
        if employee == 47:
            return 0
        else:
            return 1
        
    @api.model
    def get_tipo_pago(self, employee):
        #01 Remuneraciones del mes
        #02 Gratificaciones
        #03 Bono Ley de Modernizacion Empresas Publicas
        #TODO: en base a que se elije el tipo de pago???
        return 1
    
    @api.model
    def get_regimen_provisional(self, contract):
        if contract.pension is True:
            return 'SIP'
        else:
            return 'AFP'
    
    @api.model
    def get_tipo_trabajador(self, employee):

        if employee.type_id is False:
          return 0
        else:
            tipo_trabajador = employee.type_id

        #Codigo    Glosa
        #id_type
        #0        Activo (No Pensionado)
        #1        Pensionado y cotiza
        #2        Pensionado y no cotiza
        #3        Activo > 65 años (nunca pensionado)
        return tipo_trabajador
    
    @api.model
    def get_dias_trabajados(self, payslip):
        if payslip:
            for line in payslip.worked_days_line_ids:
                    if line.code == 'WORK100':
                        worked_days = line.number_of_days
            if worked_days > 3:
                missed_days = 0
                worked_days = 30
                for line2 in payslip.worked_days_line_ids:
                        if (line2.code == 'No_Trabajado' or line2.code == 'Licencia'):
                            missed_days = missed_days + line2.number_of_days
                worked_days = worked_days - missed_days
        return worked_days

    @api.model
    def get_regla_value(self, payslip, regla):


        if payslip:
            for line in payslip.worked_days_line_ids:
                    if line.code == 'WORK100':
                        worked_days = line.number_of_days
            if worked_days > 3:
                missed_days = 0
                worked_days = 30
                for line2 in payslip.worked_days_line_ids:
                        if (line2.code == 'No_Trabajado' or line2.code == 'Licencia'):
                            missed_days = missed_days + line2.number_of_days
                worked_days = worked_days - missed_days
        return worked_days




    @api.model
    def get_tipo_linea(self, payslip):
        #00 Linea Principal o Base
        #01 Linea Adicional
        #02 Segundo Contrato
        #03 Movimiento de Personal Afiliado Voluntario
        return '00'

    @api.model
    def get_codigo_movimiento(self, payslip):
        #Codigo Glosa 0 Sin Movimiento en el Mes 
        #1 Contratacion a plazo indefinido 
        #2 Retiro 
        #3 Subsidios 
        #4 Permiso Sin Goce de Sueldos 
        #5 Incorporacion en el Lugar de Trabajo 
        #6 Accidentes del Trabajo 
        #7 Contratacion a plazo fijo 
        #8 Cambio Contrato plazo fijo a plazo indefinido 
        #11 Otros Movimientos (Ausentismos)
        #12 Reliquidacion, Premio, Bono
        return '0'

    @api.model
    def get_tramo_asignacion_familiar(self, payslip, valor):
        try:
            if payslip.contract_id.carga_familiar != 0 and payslip.indicadores_id.asignacion_familiar_tercer >= payslip.contract_id.wage and payslip.contract_id.pension is False:
                if payslip.indicadores_id.asignacion_familiar_primer >= valor:
                    return 'A'
                elif payslip.indicadores_id.asignacion_familiar_segundo  >= valor:
                   return 'B'
                elif payslip.indicadores_id.asignacion_familiar_tercer  >= valor:
                   return 'C'
            else:
                return 'D' 
        except:
            return 'D' 
            
    
    def get_payslip_lines_value(self, obj, regla):
        try:
            linea = obj.search([('code','=',regla)])
            valor = linea.amount
            return valor 
        except:
            return '0' 

    def get_payslip_lines_value_2(self, obj, regla):
        valor = 0
        lineas = self.env['hr.payslip.line']
        detalle = lineas.search([('slip_id','=',obj.id),('code','=',regla)])
        valor = detalle.amount
        return valor        

    @api.model
    def get_imponible_afp(self, payslip, TOTIM):
        if payslip.contract_id.pension is True:
          return '0'
        elif TOTIM >=round(payslip.indicadores_id.tope_imponible_afp*payslip.indicadores_id.uf):
          return round(payslip.indicadores_id.tope_imponible_afp*payslip.indicadores_id.uf)
        else:
          return round(TOTIM)

    @api.model
    def get_imponible_mutual(self, payslip, TOTIM):
        if payslip.contract_id.mutual_seguridad is False:
          return 0
        elif payslip.contract_id.type_id.name == 'Sueldo Empresarial':
          return 0 
        elif TOTIM >=round(payslip.indicadores_id.tope_imponible_afp*payslip.indicadores_id.uf):
          return round(payslip.indicadores_id.tope_imponible_afp*payslip.indicadores_id.uf)
        else:
          return round(TOTIM)    

    @api.model
    def get_imponible_seguro_cesantia(self, payslip, TOTIM):
        if payslip.contract_id.pension is True:
            return 0
        elif payslip.contract_id.type_id.name == 'Sueldo Empresarial':
            return 0
        elif payslip.contract_id.type_id.name == 'Plazo Fijo':
            return 0 
        elif TOTIM >=round(payslip.indicadores_id.tope_imponible_seguro_cesantia*payslip.indicadores_id.uf):
            return round(payslip.indicadores_id.tope_imponible_seguro_cesantia*payslip.indicadores_id.uf) 
        elif payslip.contract_id.type_id.name == 'Plazo Indefinido':
            return round(TOTIM) 
        else:
            return 0

    @api.model
    def get_imponible_salud(self, payslip, TOTIM):
        result = 0
        if TOTIM >= round(payslip.indicadores_id.tope_imponible_afp*payslip.indicadores_id.uf):
          #return "0.0"
          return int(round(payslip.indicadores_id.tope_imponible_afp*payslip.indicadores_id.uf))
        else:
          #return 0
          return int(round(TOTIM))

    @api.model
    def _acortar_str(self, texto, size=1):
        c = 0
        cadena = ""
        while c < size and c < len(texto):
            cadena += texto[c]
            c += 1
        return cadena


    @api.model
    def _arregla_str(self, texto, size=1):
        c = 0
        cadena = ""
        special_chars = [
         [u'á', 'a'],
         [u'é', 'e'],
         [u'í', 'i'],
         [u'ó', 'o'],
         [u'ú', 'u'],
         [u'ñ', 'n'],
         [u'Á', 'A'],
         [u'É', 'E'],
         [u'Í', 'I'],
         [u'Ó', 'O'],
         [u'Ú', 'U'],
         [u'Ñ', 'N']]

        while c < size and c < len(texto):
            cadena += texto[c]
            c += 1

        
        for char in special_chars:
          try:
            cadena = cadena.replace(char[0], char[1])
          except:
            pass
        return cadena
    
    @api.multi
    def action_generate_csv(self):
        employee_model = self.env['hr.employee']
        payslip_model = self.env['hr.payslip']
        payslip_line_model = self.env['hr.payslip.line']       
        sexo_data = {'male': "M",
                     'female': "F",
                     }
        _logger = logging.getLogger(__name__)
        country_company = self.env.user.company_id.country_id
        output = io.BytesIO()
        writer = csv.writer(output, delimiter=self.delimiter, quotechar=self.quotechar, quoting=csv.QUOTE_NONNUMERIC)
        header = ["RUT", "DV",
                  "Apellido Paterno", "Apellido Materno", "Nombres", "Sexo", "Nacionalidad", 
                  "Tipo Pago", "Periodo Desde", "Periodo Hasta", 
                  "Regimen Previsional", "Tipo Trabajador", "Dias Trabajados", 
                  "Tipo de Linea", "Codigo Movimiento de Personal ", 
                  "Fecha Desde", "Fecha Hasta", 
                  "Tramo Asignacion Familiar", "N Cargas Simples", "N Cargas Maternales", "N Cargas Invalidas", 
                  "Asignacion Familiar", "Asignacion Familiar Retroactiva", 
                  "Reintegro Cargas Familiares", "Subsidio Trabajador Joven", 
                  "Codigo de la AFP", "Renta Imponible AFP", "Cotizacion Obligatoria AFP", 
                  "Cotizacion Seguro de Invalidez y Sobrevivencia (SIS)",
                  "Cuenta de Ahorro Voluntario AFP ", "Renta Imp. Sust. AFP", "Tasa Pactada (Sustit.)", "Aporte Indemn. (Sustit.) ",
                  "N Periodos (Sustit.)", "Periodo Desde (Sustit.)", "Periodo Hasta (Sustit.)", 
                  "Puesto de Trabajo Pesado", " Cotizacion Trabajo Pesado", "Cotizacion Trabajo Pesado", 
                  "Codigo de la Institucion APVI ", "Numero de Contrato APVI", "Forma de Pago APVI", "Cotizacion APV",
                  "Cotizacion Depositos Convencidos", 
                  "Codigo Institucion Autorizada APVC", "Numero de Contrato APVC", "Forma de Pago APVC",
                  "Cotizacion Trabajador APVC", "Cotizacion Empleador APVC",
                  "RUT Afiliado Voluntario", "DV Afiliado Voluntario", 
                  "Apellido Paterno", "Apellido Materno", "Nombres",
                  "Codigo Movimientode Personal", "Fecha Desde", "Fecha Hasta", 
                  "Codigo de la AFP", "Monto Capitalizacion Voluntaria", 
                  "Monto Ahorro Voluntario", "Numero de periodos de cotizacion ", 
                  "Codigo Ex-Caja Regimen", "Tasa Cotizacion Ex-Cajas de Prevision", 
                  "Renta Imponible IPS", "Cotizacion Obligatoria IPS", "Renta Imponible Desahucio",
                  "Codigo Ex-Caja Regimen Desahucio", "Tasa Cotizacion Desahucio Ex-Cajas de Prevision", 
                  "Cotizacion Desahucio", "Cotizacion Fonasa", "Cotizacion Acc. Trabajo (ISL)", 
                  "Bonificacion Ley 15.386", "Descuento por cargas familiares (ISL)", 
                  "Bonos de Gobierno ", "Codigo Institucion de Salud", 
                  "Numero de FUN", "Renta Imponible Isapre", "Moneda del plan pactado Isapre",
                  "Cotizacion Pactada", "Cotizacion Obligatoria Isapre", "Cotizacion Adicional Voluntaria", 
                  "Monto GES (Futuro)", "Codigo CCAF", "Renta Imponible CCAF", 
                  "Creditos Personales CCAF", "Descuento Dental CCAF ", 
                  "Descuentos por Leasing (Programa de Ahorro) ", 
                  "Descuentos por seguro de vida CCAF ", "Otros descuentos CCAF",
                  "Cotizacion a CCAF de no afiliados a Isapres", "Descuento Cargas Familiares CCAF", 
                  "Otros descuentos CCAF 1 (Futuro)", "Otros descuentos CCAF 2 (Futuro)", 
                  "Bonos Gobierno (Futuro)", "Codigo de Sucursal (Futuro)", 
                  "Codigo Mutualidad", "Renta Imponible Mutual", 
                  "Cotizacion Accidente del Trabajo (MUTUAL)", "Sucursal para pago Mutual", 
                  "Renta Imponible Seguro Cesantia (Informar Renta Total Imponible)",
                  "Aporte Trabajador Seguro Cesantia", "Aporte Empleador Seguro Cesantia", 
                  "Rut Pagadora Subsidio", "DV Pagadora Subsidio", 
                  "Centro de Costos", "Sucursal", "Agencia", "Obra", "Region"
                  ]
        #writer.writerow(header)
        
        
        
        #Debemos colocar que tome todo el mes y no solo el día exacto TODO
        payslip_recs = payslip_model.search([('date_from','=',self.date_from),
                                             ])

        date_start = self.date_from
        date_stop = self.date_to
        date_start_format = datetime.strptime(date_start, DF).strftime("%m%Y")
        date_stop_format = datetime.strptime(date_stop, DF).strftime("%m%Y")
        line_employee = []
        rut = ""
        rut_dv = ""
        rut_emp = ""
        rut_emp_dv = ""

        try:
            rut_emp, rut_emp_dv = self.env.user.company_id.vat.split("-")
            rut_emp = rut_emp.replace('.','')
        except:
            pass  


        for payslip in payslip_recs:
            payslip_line_recs = payslip_line_model.search([('slip_id','=',payslip.id)])
            rut = ""
            rut_dv = ""
            rut, rut_dv = payslip.employee_id.identification_id.split("-")
            rut = rut.replace('.','')
            line_employee = [self._acortar_str(rut, 11), 
                             self._acortar_str(rut_dv, 1),
                             self._arregla_str(payslip.employee_id.last_name.upper(), 30)  if payslip.employee_id.last_name else "", 
                             self._arregla_str(payslip.employee_id.mothers_name.upper(), 30)  if payslip.employee_id.mothers_name else "",
                             "%s %s" % (self._arregla_str(payslip.employee_id.name.upper(), 15), self._arregla_str(payslip.employee_id.middle_name.upper(), 15) if payslip.employee_id.middle_name else ''),
                             sexo_data.get(payslip.employee_id.gender, "") if payslip.employee_id.gender else "",
                             self.get_nacionalidad(payslip.employee_id.country_id.id),
                             self.get_tipo_pago(payslip.employee_id),
                             date_start_format,
                             date_stop_format,
                             #11
                             self.get_regimen_provisional(payslip.contract_id),
                             #12
                             self.get_tipo_trabajador(payslip.employee_id),
                             #13
                             int(self.get_dias_trabajados(payslip and payslip[0] or False)),
                             #14
                             self.get_tipo_linea(payslip and payslip[0] or False),
                             #15
                             payslip.movimientos_personal,
                             #16 Fecha inicio movimiento personal (dia-mes-año)
                             datetime.strptime(payslip.date_from, DF).strftime("%d/%m/%Y") if payslip.date_from else '00/00/0000', 
                             #payslip.date_from if payslip.date_from else '00/00/0000', 
                             #17 Fecha fin movimiento personal (dia-mes-año)
                             datetime.strptime(payslip.date_to, DF).strftime("%d/%m/%Y") if payslip.date_to else '00/00/0000', 
                             #payslip.date_to if payslip.date_to else '00-00-0000', 
                             self.get_tramo_asignacion_familiar(payslip, self.get_payslip_lines_value_2(payslip,'TOTIM')),
                             #19 NCargas Simples
                             payslip.contract_id.carga_familiar,
                             payslip.contract_id.carga_familiar_maternal,
                             payslip.contract_id.carga_familiar_invalida,
                             #22 Asignacion Familiar
                             self.get_payslip_lines_value_2(payslip,'ASIGFAM') if self.get_payslip_lines_value_2(payslip,'ASIGFAM') else "00",
                             #ASIGNACION FAMILIAR RETROACTIVA
                             "0",
                             #Reintegro Cargas Familiares
                             "0",
                             #25 Solicitud Trabajador Joven TODO SUBSIDIO JOVEN
                             "N",
                             #26
                             payslip.contract_id.afp_id.codigo,
                             #27
                             int(self.get_imponible_afp(payslip and payslip[0] or False, self.get_payslip_lines_value_2(payslip,'TOTIM'))),
                             #AFP SIS APV 0 0 0 0 0 0
                             #28 
                             self.get_payslip_lines_value_2(payslip,'PREV'),
                             self.get_payslip_lines_value_2(payslip,'SIS'),
                             self.get_payslip_lines_value_2(payslip,'APV') if self.get_payslip_lines_value_2(payslip,'APV') else "0",
                             #31 Renta Imp. Sust.AFP
                             "0",
                             #32 Tasa Pactada (Sustit.)
                             "0",
                             #33 Aporte Indemn. (Sustit.)
                             "0",
                             #34 N Periodos (Sustit.)
                             "0",
                             #35 Periodo desde (Sustit.)
                             "0",
                             #36 Periodo Hasta (Sustit.)
                             "0",
                             #37 Puesto de Trabajo Pesado
                             " ",
                             #38 % Cotizacion Trabajo Pesado
                             "0",
                             #39 Cotizacion Trabajo Pesado
                             "0",
                             #3- Datos Ahorro Previsional Voluntario Individual
                             #40 Codigo de la Institucion APVI TODO
                             "0" + payslip.contract_id.afp_id.codigo if self.get_payslip_lines_value_2(payslip,'APV') else "0"
                             #41 Numero de Contrato APVI Strinng
                             "0",
                             #42 Forma de Pago Ahorro
                             "0",
                             #43 Cotizacion Ahorro Previsional 
                             "0",
                             #44 Cotizacion Depositos 
                             "0",
                             #45 Codigo Institucion Autorizada APVC
                             "0",
                             #46 Numero de Contrato APVC TODO
                             " ",
                             #47 Forma de Pago APVC
                             "0",
                             #48 Cotizacion Trabajador APVC 
                             "0",
                             #49 Cotizacion Empleador APVC 
                             "0",
                             #50 RUT Afiliado Voluntario 9 (11)
                             "0",
                             #51 DV Afiliado Voluntario
                             " ",
                             #52 Apellido Paterno
                             " ",
                             #53 Apellido Materno 
                             " ",
                             #54 Nombres
                             " ",
                             "0",
                             #55 Codigo Movimiento de Persona
                             #Tabla N°7: Movimiento de Personal
                             #Código Glosa
                             #0 Sin Movimiento en el Mes
                             #1 Contratación a plazo indefinido
                             #2 Retiro
                             #3 Subsidios
                             #4 Permiso Sin Goce de Sueldos
                             #5 Incorporación en el Lugar de Trabajo
                             #6 Accidentes del Trabajo
                             #7 Contratación a plazo fijo
                             #8 Cambio Contrato plazo fijo a plazo indefinido
                             #11 Otros Movimientos (Ausentismos)
                             #12 Reliquidación, Premio, Bono
                             #TODO LIQUIDACION
                             
                             "00",            
                             #56 Fecha inicio movimiento personal (dia-mes-año)
                             "0",
                             #57 Fecha fin movimiento personal (dia-mes-año)
                             "0",
                             #58 Codigo de la AFP
                             "0",
                             #59 Monto Capitalizacion Voluntaria
                             "0",
                             #60 Monto Ahorro Voluntario
                             "0",
                     
                             #61 Numero de periodos de cotizacion
                             "0",
                             #62 Codigo EX-Caja Regimen
                             "0",
                             #63 Tasa Cotizacion Ex-Caja Prevision
                             "0",
                             #64 Renta Imponible IPS    Obligatorio si es IPS Obligatorio si es IPS Obligatorio si es INP si no, 0000
                             self.get_payslip_lines_value_2(payslip,'TOTIM') if payslip.contract_id.isapre_id.codigo=='07' else "0",
                             #65 Cotizacion Obligatoria IPS 
                             "0",
                             #66 Renta Imponible Desahucio
                             "0",
                             #67 Codigo Ex-Caja Regimen Desahucio
                             "0",
                             #68 Tasa Cotizacion Desahucio Ex-Cajas
                             "0",
                             #69 Cotizacion Desahucio
                             "0",
                             #70 Cotizacion Fonasa
                             #"0",
                             self.get_payslip_lines_value_2(payslip,'FONASA') if payslip.contract_id.isapre_id.codigo=='07' else "0",
                             
                             #71 Cotizacion Acc. Trabajo (ISL)
                             "0",
                             #72 Bonificacion Ley 15.386 
                             "0",
                             #73 Descuento por cargas familiares de ISL
                             "0",
                             #74 Bonos Gobierno
                             "0",
                             #7- Datos Salud ISAPRE
                             #75 Codigo Institucion de Salud 
                             payslip.contract_id.isapre_id.codigo,
                             #76 Numero del FUN
                             " " if payslip.contract_id.isapre_id.codigo=='07' else payslip.contract_id.isapre_fun if payslip.contract_id.isapre_fun else "",
                             #77 Renta Imponible Isapre REVISAR  Tope Imponible Salud 5,201
                             #"0" if payslip.contract_id.isapre_id.codigo=='07' else self.get_payslip_lines_value_2(payslip,'TOTIM'),
                             "0" if payslip.contract_id.isapre_id.codigo=='07' else self.get_imponible_salud(payslip and payslip[0] or False, self.get_payslip_lines_value_2(payslip,'TOTIM')),
                             #78 Moneda Plan Isapre UF Pesos TODO Poner % Pesos o UF
                             #Tabla N17: Tipo Moneda del plan pactado Isapre
                             #Codigo Glosa
                             #1 Pesos
                             #2 UF
                             "1" if payslip.contract_id.isapre_id.codigo=='07' else "2",
                             #79 Cotizacion Pactada
                             # Yo Pensaba payslip.contract_id.isapre_cotizacion_uf,
                             "0" if payslip.contract_id.isapre_id.codigo=='07' else payslip.contract_id.isapre_cotizacion_uf,
                             #80 Cotizacion Obligatoria Isapre
                             "0" if payslip.contract_id.isapre_id.codigo=='07' else self.get_payslip_lines_value_2(payslip,'SALUD'),
                             #81 Cotizacion Adicional Voluntaria
                             "0" if payslip.contract_id.isapre_id.codigo=='07' else self.get_payslip_lines_value_2(payslip,'ADISA'),
                             #82 Monto Garantia Explicita de Salud
                             "0",
                             #8- Datos Caja de Compensacion
                             #83 Codigo CCAF 
                             #TODO ES HACER PANTALLA CON DATOS EMPRESA
                             payslip.indicadores_id.ccaf_id.codigo if payslip.indicadores_id.ccaf_id.codigo else "00",
                             #84 Renta Imponible CCAF 
                             int(self.get_imponible_afp(payslip and payslip[0] or False, self.get_payslip_lines_value_2(payslip,'TOTIM'))) if (self.get_dias_trabajados(payslip and payslip[0] or False)>0) else "00",
                             #85 Creditos Personales CCAF TODO
                             self.get_payslip_lines_value_2(payslip,'PCCAF') if self.get_payslip_lines_value_2(payslip,'PCCAF') else "0",
                             #86 Descuento Dental CCAF
                             "0",
                             #87 Descuentos por Leasing TODO
                             "0",
                             #88 Descuentos por seguro de vida TODO
                             "0",
                             #89 Otros descuentos CCAF 
                             "0",
                             #90 Cotizacion a CCAF de no afiliados a Isapres
                             self.get_payslip_lines_value_2(payslip,'CAJACOMP') if self.get_payslip_lines_value_2(payslip,'CAJACOMP') else "0",
                             #91 Descuento Cargas Familiares CCAF
                             "0",
                             #92 Otros descuentos CCAF 1 (Uso Futuro)
                             "0",
                             #93 Otros descuentos CCAF 2 (Uso Futuro) 
                             "0",
                             #94 Bonos Gobierno (Uso Futuro) 
                             "0",
                             #9- Datos Mutualidad
                             #95 Codigo de Sucursal (Uso Futuro)
                             " ",
                             #96 Codigo Mutualidad
                             payslip.indicadores_id.mutualidad_id.codigo if payslip.indicadores_id.mutualidad_id.codigo else "00",
                             #97 Renta Imponible Mutual TODO Si afiliado hacer
                             self.get_imponible_mutual(payslip and payslip[0] or False, self.get_payslip_lines_value_2(payslip,'TOTIM')),
                             #98 Cotizacion Accidente del Trabajo
                             self.get_payslip_lines_value_2(payslip,'MUT') if self.get_payslip_lines_value_2(payslip,'MUT') else "0",
                             #99 Codigo de Sucursal (Uso Futuro)
                             "0",
                             #10- Datos Administradora de Seguro de Cesantia
                             #100 Renta Imponible Seguro Cesantia 
                             self.get_imponible_seguro_cesantia(payslip and payslip[0] or False, self.get_payslip_lines_value_2(payslip,'TOTIM')),
                             #101 Aporte Trabajador Seguro Cesantia
                             self.get_payslip_lines_value_2(payslip,'SECE') if self.get_payslip_lines_value_2(payslip,'SECE') else "0",
                             #102 Aporte Empleador Seguro Cesantia
                             self.get_payslip_lines_value_2(payslip,'SECEEMP') if self.get_payslip_lines_value_2(payslip,'SECEEMP') else "0",
                             #103 Rut Pagadora Subsidio
                             # yo pensaba rut_emp,
                             "0",
                             #104 DV Pagadora Subsidio
                             # yo pensaba rut_emp_dv,
                             "",
                             #105 Centro de Costos, Sucursal, Agencia 
                             "1"
                             ]
            writer.writerow(line_employee)
        self.write({'file_data': base64.encodestring(output.getvalue()),
                    'file_name': "Previred_%s.txt" % (self.date_to),
                    })
        return self.show_view('Previred Generado', self._name, 'l10n_cl_hr_payroll.wizard_export_csv_previred_form_view', self.id)
