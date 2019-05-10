
import io
import csv
import base64
import logging
import time
from datetime import datetime
from dateutil import relativedelta

from odoo import models, api, fields
import odoo.addons.decimal_precision as dp
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

class WizardExportCsvPrevired(models.TransientModel):

    _name = 'wizard.export.csv.previred'
    _description = 'wizard.export.csv.previred'
    
    delimiter = {
        'comma':  ',',
        'dot_coma':  ';',
        'tab':  '\t',
    }
    quotechar = {
        'colon':  '"',
        'semicolon':  "'",
        'none':  '',
    } 
    
    date_from = fields.Date('Fecha Inicial', required=True, default=lambda self: time.strftime('%Y-%m-01'))
    date_to = fields.Date('Fecha Final', required=True, default=lambda self: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])
    file_data = fields.Binary('Archivo Generado')
    file_name = fields.Char('Nombre de archivo')
    delimiter_option = fields.Selection([
        ('colon','Comillas Dobles(")'),
        ('semicolon',"Comillas Simples(')"),
        ('none',"Ninguno"),
        ], string='Separador de Texto', default='colon', required=True)
    delimiter_field_option = fields.Selection([
        ('comma','Coma(,)'),
        ('dot_coma',"Punto y coma(;)"),
        ('tab',"Tabulador"),
        ], string='Separador de Campos', default='dot_coma', required=True)
    
    @api.multi
    def show_view(self, name):
        search_ids = self.env['wizard.export.csv.previred'].search([])
        last_id = search_ids and max(search_ids)        
        return {
            'name': name,
            'context': self._context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.export.csv.previred',
            'res_id': last_id.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    @api.model
    def get_nacionalidad(self, employee):
        #0 chileno, 1 extranjero, comparar con el pais de la compañia
        if employee == 46:
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
            tipo_trabajador = employee.type_id.id_type

        #Codigo    Glosa
        #id_type
        #0        Activo (No Pensionado)
        #1        Pensionado y cotiza
        #2        Pensionado y no cotiza
        #3        Activo > 65 años (nunca pensionado)
        return tipo_trabajador
    
    @api.model
    def get_dias_trabajados(self, payslip):
        worked_days = 0
        if payslip:
            for line in payslip.worked_days_line_ids:
                    if line.code == 'WORK100':
                        worked_days = line.number_of_days
        return worked_days

    @api.model
    def get_cost_center(self, contract):
        cost_center = "1"
        if contract.analytic_account_id:
            cost_center = contract.analytic_account_id.code
        return cost_center


    @api.model
    def get_tipo_linea(self, payslip):
        #00 Linea Principal o Base
        #01 Linea Adicional
        #02 Segundo Contrato
        #03 Movimiento de Personal Afiliado Voluntario
        return '00'


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
    def get_imponible_afp_2(self, payslip, TOTIM, LIC):
        if LIC > 0:
            TOTIM=LIC
        if payslip.contract_id.pension is True:
            return '0'
        elif TOTIM >=round(payslip.indicadores_id.tope_imponible_afp*payslip.indicadores_id.uf):
            return int(round(payslip.indicadores_id.tope_imponible_afp*payslip.indicadores_id.uf))      
        else:
            return int(round(TOTIM))

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
    def get_imponible_seguro_cesantia(self, payslip, TOTIM, LIC):
        if LIC > 0:
            TOTIM=LIC
        if payslip.contract_id.pension is True:
            return 0
        elif payslip.contract_id.type_id.name == 'Sueldo Empresarial':
            return 0
        elif TOTIM >=round(payslip.indicadores_id.tope_imponible_seguro_cesantia*payslip.indicadores_id.uf):
            return int(round(payslip.indicadores_id.tope_imponible_seguro_cesantia*payslip.indicadores_id.uf))
        else:
            return int(round(TOTIM))

    @api.model
    def get_imponible_salud(self, payslip, TOTIM):
        result = 0
        if TOTIM >= round(payslip.indicadores_id.tope_imponible_afp*payslip.indicadores_id.uf):
            return int(round(payslip.indicadores_id.tope_imponible_afp*payslip.indicadores_id.uf))
        else:
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
         ['á', 'a'],
         ['é', 'e'],
         ['í', 'i'],
         ['ó', 'o'],
         ['ú', 'u'],
         ['ñ', 'n'],
         ['Á', 'A'],
         ['É', 'E'],
         ['Í', 'I'],
         ['Ó', 'O'],
         ['Ú', 'U'],
         ['Ñ', 'N']]

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
        output = io.StringIO()
        if self.delimiter_option == 'none':
            writer = csv.writer(output, delimiter=self.delimiter[self.delimiter_field_option], quoting=csv.QUOTE_NONE)
        else:
            writer = csv.writer(output, delimiter=self.delimiter[self.delimiter_field_option], quotechar=self.quotechar[self.delimiter_option], quoting=csv.QUOTE_NONE)
        #Debemos colocar que tome todo el mes y no solo el día exacto TODO
        payslip_recs = payslip_model.search([('date_from','=',self.date_from),
                                             ])

        date_start = self.date_from
        date_stop = self.date_to
        date_start_format = date_start.strftime("%m%Y")
        date_stop_format = date_stop.strftime("%m%Y")
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
                             "%s %s" % (self._arregla_str(payslip.employee_id.firstname.upper(), 15), self._arregla_str(payslip.employee_id.middle_name.upper(), 15) if payslip.employee_id.middle_name else ''),
                             sexo_data.get(payslip.employee_id.gender, "") if payslip.employee_id.gender else "",
                             self.get_nacionalidad(payslip.employee_id.country_id.id),
                             self.get_tipo_pago(payslip.employee_id),
                             date_start_format,
                             date_stop_format,
                             #11
                             self.get_regimen_provisional(payslip.contract_id),
                             #12
                             "0",
                             #payslip.employee_id.type_id.id_type,
                             #13
                             int(self.get_dias_trabajados(payslip and payslip[0] or False)),
                             #14
                             self.get_tipo_linea(payslip and payslip[0] or False),
                             #15
                             payslip.movimientos_personal,
                             #16 Fecha inicio movimiento personal (dia-mes-año)
                             #Si declara mov. personal 1, 3, 4, 5, 6, 7, 8 y 11 Fecha Desde
                             #es obligatoria y debe estar dentro del periodo de remun
                             payslip.date_from.strftime("%d/%m/%Y") if payslip.movimientos_personal != '0' else '00/00/0000', 
                             #payslip.date_from if payslip.date_from else '00/00/0000', 
                             #17 Fecha fin movimiento personal (dia-mes-año)
                             payslip.date_to.strftime("%d/%m/%Y") if payslip.movimientos_personal != '0' else '00/00/0000', 
                             #Si declara mov. personal 1, 3, 4, 5, 6, 7, 8 y 11 Fecha Desde
                             #es obligatoria y debe estar dentro del periodo de remun
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
                             int(self.get_imponible_afp_2(payslip and payslip[0] or False, self.get_payslip_lines_value_2(payslip,'TOTIM'), self.get_payslip_lines_value_2(payslip,'IMPLIC'))),
                             #AFP SIS APV 0 0 0 0 0 0
                             #28 
                             int(self.get_payslip_lines_value_2(payslip,'PREV')),
                             int(self.get_payslip_lines_value_2(payslip,'SIS')),
                             #30 Cuenta de Ahorro Voluntario AFP
                             "0",
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
                             #40 Código de la Institución APVI
                             payslip.contract_id.apv_id.codigo if self.get_payslip_lines_value_2(payslip,'APV') else "0",
                             #41 Numero de Contrato APVI Strinng
                             "0",
                             #42 Forma de Pago Ahorro
                             payslip.contract_id.forma_pago_apv if self.get_payslip_lines_value_2(payslip,'APV') else "0",
                             #43 Cotización APVI 9(8) Monto en $ de la Cotización APVI
                             int(self.get_payslip_lines_value_2(payslip,'APV')) if self.get_payslip_lines_value_2(payslip,'APV') else "0",
                             #44 Cotizacion Depositos 
                             
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
                             int(self.get_payslip_lines_value_2(payslip,'ISL')) if self.get_payslip_lines_value_2(payslip,'ISL') else "0",


                           #0.93% de la Rta. Imp. (64) y es obligatorio para
#el empleador. Se paga a través de ISL sólo en
#casos en que no exista Mutual Asociada En otro
#caso se paga en la mutual respectiva. Datos no numérico 
 
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
                             "0" if payslip.contract_id.isapre_id.codigo=='07' else int(self.get_payslip_lines_value_2(payslip,'SALUD')),
                             #81 Cotizacion Adicional Voluntaria
                             "0" if payslip.contract_id.isapre_id.codigo=='07' else int(self.get_payslip_lines_value_2(payslip,'ADISA')),
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
                             int(self.get_payslip_lines_value_2(payslip,'MUT')) if self.get_payslip_lines_value_2(payslip,'MUT') else "0",
                             #99 Codigo de Sucursal (Uso Futuro)
                             "0",
                             #10- Datos Administradora de Seguro de Cesantia
                             self.get_imponible_seguro_cesantia(payslip and payslip[0] or False, self.get_payslip_lines_value_2(payslip,'TOTIM') , self.get_payslip_lines_value_2(payslip,'IMPLIC')),
                             #101 Aporte Trabajador Seguro Cesantia
                             int(self.get_payslip_lines_value_2(payslip,'SECE')) if self.get_payslip_lines_value_2(payslip,'SECE') else "0",
                             #102 Aporte Empleador Seguro Cesantia
                             int(self.get_payslip_lines_value_2(payslip,'SECEEMP')) if self.get_payslip_lines_value_2(payslip,'SECEEMP') else "0",
                             #103 Rut Pagadora Subsidio
                             # yo pensaba rut_emp,
                             "0",
                             #104 DV Pagadora Subsidio
                             # yo pensaba rut_emp_dv,
                             "",
                             #105 Centro de Costos, Sucursal, Agencia 
                             int(self.get_cost_center(payslip.contract_id)),
                             ]
            writer.writerow([str(l) for l in line_employee])
        self.write({'file_data': base64.encodebytes(output.getvalue().encode()),
                    'file_name': "Previred_%s.txt" % (self.date_to),
                    })
                
        return self.show_view(u'Previred Generado')
