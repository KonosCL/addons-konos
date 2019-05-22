from odoo import api, fields, models, tools, _
from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import requests


_logger = logging.getLogger(__name__)
MONTH_LIST= [('1', 'Enero'), 
        ('2', 'Febrero'), ('3', 'Marzo'), 
        ('4', 'Abril'), ('5', 'Mayo'), 
        ('6', 'Junio'), ('7', 'Julio'), 
        ('8', 'Agosto'), ('9', 'Septiembre'), 
        ('10', 'Octubre'), ('11', 'Noviembre'),
        ('12', 'Diciembre')]

STATES = {'draft': [('readonly', False)]}

class hr_indicadores_previsionales(models.Model):

    _name = 'hr.indicadores'
    _description = 'Indicadores Previsionales'

    name = fields.Char('Nombre')
    state = fields.Selection([
        ('draft','Borrador'),
        ('done','Validado'),
        ], string=u'Estado', readonly=True, default='draft')
    asignacion_familiar_primer = fields.Float(
        'Asignación Familiar Tramo 1', 
        readonly=True, states=STATES,
        help="Asig Familiar Primer Tramo")
    asignacion_familiar_segundo = fields.Float(
        'Asignación Familiar Tramo 2', 
        readonly=True, states=STATES,
        help="Asig Familiar Segundo Tramo")
    asignacion_familiar_tercer = fields.Float(
        'Asignación Familiar Tramo 3', 
        readonly=True, states=STATES,
        help="Asig Familiar Tercer Tramo")
    asignacion_familiar_monto_a = fields.Float(
        'Monto Tramo Uno', readonly=True, states=STATES, help="Monto A")
    asignacion_familiar_monto_b = fields.Float(
        'Monto Tramo Dos', readonly=True, states=STATES, help="Monto B")
    asignacion_familiar_monto_c = fields.Float(
        'Monto Tramo Tres', readonly=True, states=STATES, help="Monto C")
    contrato_plazo_fijo_empleador = fields.Float(
        'Contrato Plazo Fijo Empleador', 
        readonly=True, states=STATES,
        help="Contrato Plazo Fijo Empleador")
    contrato_plazo_fijo_trabajador = fields.Float(
        'Contrato Plazo Fijo Trabajador', 
        readonly=True, states=STATES,
        help="Contrato Plazo Fijo Trabajador")    
    contrato_plazo_indefinido_empleador = fields.Float(
        'Contrato Plazo Indefinido Empleador', 
        readonly=True, states=STATES,
        help="Contrato Plazo Fijo")
    contrato_plazo_indefinido_empleador_otro = fields.Float(
        'Contrato Plazo Indefinido 11 anos o mas', 
        readonly=True, states=STATES,
        help="Contrato Plazo Indefinido 11 anos Empleador")
    contrato_plazo_indefinido_trabajador_otro = fields.Float(
        'Contrato Plazo Indefinido 11 anos o mas', 
        readonly=True, states=STATES,
        help="Contrato Plazo Indefinido 11 anos Trabajador")
    contrato_plazo_indefinido_trabajador = fields.Float(
        'Contrato Plazo Indefinido Trabajador', 
        readonly=True, states=STATES,
        help="Contrato Plazo Indefinido Trabajador")
    caja_compensacion = fields.Float(
        'Caja Compensación', 
        readonly=True, states=STATES,
        help="Caja de Compensacion")
    deposito_convenido = fields.Float(
        'Deposito Convenido', readonly=True, states=STATES, help="Deposito Convenido")
    fonasa = fields.Float('Fonasa', readonly=True, states=STATES, help="Fonasa")
    mutual_seguridad = fields.Float(
        'Mutualidad', readonly=True, states=STATES, help="Mutual de Seguridad")
    isl = fields.Float(
        'ISL', readonly=True, states=STATES, help="Instituto de Seguridad Laboral")
    pensiones_ips = fields.Float(
        'Pensiones IPS', readonly=True, states=STATES, help="Pensiones IPS")
    sueldo_minimo = fields.Float(
        'Trab. Dependientes e Independientes', readonly=True, states=STATES, help="Sueldo Minimo")
    sueldo_minimo_otro = fields.Float(
        'Menores de 18 y Mayores de 65:', 
        readonly=True, states=STATES,
        help="Sueldo Mínimo para Menores de 18 y Mayores a 65")
    tasa_afp_cuprum = fields.Float(
        'Cuprum', readonly=True, states=STATES, help="Tasa AFP Cuprum")
    tasa_afp_capital = fields.Float(
        'Capital', readonly=True, states=STATES, help="Tasa AFP Capital")
    tasa_afp_provida = fields.Float(
        'ProVida', readonly=True, states=STATES, help="Tasa AFP Provida")
    tasa_afp_modelo = fields.Float(
        'Modelo', readonly=True, states=STATES, help="Tasa AFP Modelo")
    tasa_afp_planvital = fields.Float(
        'PlanVital', readonly=True, states=STATES, help="Tasa AFP PlanVital")
    tasa_afp_habitat = fields.Float(
        'Habitat', readonly=True, states=STATES, help="Tasa AFP Habitat")
    tasa_sis_cuprum = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa SIS Cuprum")
    tasa_sis_capital = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa SIS Capital")
    tasa_sis_provida = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa SIS Provida")
    tasa_sis_planvital = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa SIS PlanVital")
    tasa_sis_habitat = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa SIS Habitat")
    tasa_sis_modelo = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa SIS Modelo")
    tasa_independiente_cuprum = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa Independientes Cuprum")
    tasa_independiente_capital = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa Independientes Capital")
    tasa_independiente_provida = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa Independientes Provida")
    tasa_independiente_planvital = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa Independientes PlanVital")
    tasa_independiente_habitat = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa Independientes Habitat")
    tasa_independiente_modelo = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa Independientes Modelo")
    tope_anual_apv = fields.Float(
        'Tope Anual APV', readonly=True, states=STATES, help="Tope Anual APV")
    tope_mensual_apv = fields.Float(
        'Tope Mensual APV', readonly=True, states=STATES, help="Tope Mensual APV")
    tope_imponible_afp = fields.Float(
        'Tope imponible AFP', readonly=True, states=STATES, help="Tope Imponible AFP")
    tope_imponible_ips = fields.Float(
        'Tope Imponible IPS', readonly=True, states=STATES, help="Tope Imponible IPS")
    tope_imponible_salud = fields.Float(
        'Tope Imponible Salud', readonly=True, states=STATES,)
    tope_imponible_seguro_cesantia = fields.Float(
        'Tope Imponible Seguro Cesantía', 
        readonly=True, states=STATES,
        help="Tope Imponible Seguro de Cesantía")
    uf = fields.Float(
        'UF',  required=True, readonly=True, states=STATES, help="UF fin de Mes")
    utm = fields.Float(
        'UTM',  required=True, readonly=True, states=STATES, help="UTM Fin de Mes")
    uta = fields.Float('UTA', readonly=True, states=STATES, help="UTA Fin de Mes")
    uf_otros = fields.Float(
        'UF Otros', readonly=True, states=STATES, help="UF Seguro Complementario")
    mutualidad_id = fields.Many2one('hr.mutual', 'MUTUAL', readonly=True, states=STATES)
    ccaf_id = fields.Many2one('hr.ccaf', 'CCAF', readonly=True, states=STATES)
    month = fields.Selection(MONTH_LIST, string='Mes', required=True, readonly=True, states=STATES)
    year = fields.Integer('Año', required=True, default=datetime.now().strftime('%Y'), readonly=True, states=STATES)
    gratificacion_legal = fields.Boolean('Gratificación L. Manual', readonly=True, states=STATES)
    mutual_seguridad_bool = fields.Boolean('Mutual Seguridad', default=True, readonly=True, states=STATES)
    ipc = fields.Float(
        'IPC',  required=True, readonly=True, states=STATES, help="Indice de Precios al Consumidor (IPC)")
    
    @api.multi
    def action_done(self):
        self.write({'state': 'done'})
        return True
    
    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    @api.onchange('month')
    def get_name(self):
        self.name = str(self.month).replace('10', 'Octubre').replace('11', 'Noviembre').replace('12', 'Diciembre').replace('1', 'Enero').replace('2', 'Febrero').replace('3', 'Marzo').replace('4', 'Abril').replace('5', 'Mayo').replace('6', 'Junio').replace('7', 'Julio').replace('8', 'Agosto').replace('9', 'Septiembre') + " " + str(self.year)

    def find_between_r(self, s, first, last ):
        try:
            start = s.rindex( first ) + len( first )
            end = s.rindex( last, start )
            return s[start:end]
        except ValueError:
            return ""

    def find_month(self, s):
        if s == '1':
            return 'Enero'
        if s == '2':
            return 'Febrero'
        if s == '3':
            return 'Marzo'
        if s == '4':
            return 'Abril'
        if s == '5':
            return 'Mayo'
        if s == '6':
            return 'Junio'
        if s == '7':
            return 'Julio'
        if s == '8':
            return 'Agosto'
        if s == '9':
            return 'Septiembre'
        if s == '10':
            return 'Octubre'
        if s == '11':
            return 'Noviembre'
        if s == '12':
            return 'Diciembre'



    @api.one
    def update_document(self):
        self.update_date = datetime.today()
        try:
            html_doc = urlopen('https://www.previred.com/web/previred/indicadores-previsionales').read()
            soup = BeautifulSoup(html_doc, 'html.parser')

            letters = soup.find_all("table")

            def clear_string(cad):
                cad = cad.replace(".", '').replace("$", '').replace(" ", '')
                cad = cad.replace("Renta", '').replace("<", '').replace(">", '')
                cad = cad.replace("=", '').replace("R", '').replace("I", '').replace("%", '')
                cad = cad.replace(",", '.')
                cad = cad.replace("1ff8","")
                return cad
        except ValueError:
            return ""

        def string_divide(cad, cad2, rounded):
            return round(float(cad) / float(cad2), rounded)


        try:
            # UF
            self.uf = clear_string(letters[0].select("strong")[1].get_text())

            # 1 UTM
            self.utm = clear_string(letters[1].select("strong")[3].get_text())

            # 1 UTA
            self.uta = clear_string(letters[1].select("strong")[4].get_text())

            # 3 RENTAS TOPES IMPONIBLES UF
            self.tope_imponible_afp = string_divide(clear_string(letters[2].select("strong")[1].get_text()), self.uf, 2)
            self.tope_imponible_ips = string_divide(clear_string(letters[2].select("strong")[2].get_text()), self.uf, 2)
            self.tope_imponible_seguro_cesantia = string_divide(clear_string(letters[2].select("strong")[3].get_text()),
                                                                self.uf, 2)

            # 4 RENTAS TOPES IMPONIBLES
            self.sueldo_minimo = clear_string(letters[3].select("strong")[1].get_text())
            self.sueldo_minimo_otro = clear_string(letters[3].select("strong")[2].get_text())

            # Ahorro Previsional Voluntario
            self.tope_mensual_apv = string_divide(clear_string(letters[4].select("strong")[2].get_text()), self.uf, 2)
            self.tope_anual_apv = string_divide(clear_string(letters[4].select("strong")[1].get_text()), self.uf, 2)

            # 5 DEPÓSITO CONVENIDO
            self.deposito_convenido = string_divide(clear_string(letters[5].select("strong")[1].get_text()), self.uf, 2)

            # 6 RENTAS TOPES IMPONIBLES
            self.contrato_plazo_indefinido_empleador = clear_string(letters[6].select("strong")[5].get_text())
            self.contrato_plazo_indefinido_trabajador = clear_string(letters[6].select("strong")[6].get_text())
            self.contrato_plazo_fijo_empleador = clear_string(letters[6].select("strong")[7].get_text())
            self.contrato_plazo_indefinido_empleador_otro = clear_string(letters[6].select("strong")[9].get_text())

            # 7 ASIGNACIÓN FAMILIAR
            self.asignacion_familiar_monto_a = clear_string(letters[8].select("strong")[4].get_text())
            self.asignacion_familiar_monto_b = clear_string(letters[8].select("strong")[6].get_text())
            self.asignacion_familiar_monto_c = clear_string(letters[8].select("strong")[8].get_text())

            self.asignacion_familiar_primer = clear_string(letters[8].select("strong")[5].get_text())[1:]
            self.asignacion_familiar_segundo = clear_string(letters[8].select("strong")[7].get_text())[6:]
            self.asignacion_familiar_tercer = clear_string(letters[8].select("strong")[9].get_text())[6:]

            # 8 TASA COTIZACIÓN OBLIGATORIO AFP
            self.tasa_afp_capital = clear_string(letters[7].select("strong")[8].get_text())
            self.tasa_sis_capital = clear_string(letters[7].select("strong")[9].get_text())

            self.tasa_afp_cuprum = clear_string(letters[7].select("strong")[11].get_text().replace(" ", '').replace("%", '').replace("1ff8", ''))
            self.tasa_sis_cuprum = clear_string(letters[7].select("strong")[12].get_text())

            self.tasa_afp_habitat = clear_string(letters[7].select("strong")[14].get_text())
            self.tasa_sis_habitat = clear_string(letters[7].select("strong")[15].get_text())

            self.tasa_afp_planvital = clear_string(letters[7].select("strong")[17].get_text())
            self.tasa_sis_planvital = clear_string(letters[7].select("strong")[18].get_text())

            self.tasa_afp_provida = clear_string(letters[7].select("strong")[20].get_text().replace(" ", '').replace("%", '').replace("1ff8", ''))
            self.tasa_sis_provida = clear_string(letters[7].select("strong")[21].get_text())

            self.tasa_afp_modelo = clear_string(letters[7].select("strong")[23].get_text())
            self.tasa_sis_modelo = clear_string(letters[7].select("strong")[24].get_text())

            self.tasa_independiente_capital = clear_string(letters[7].select("strong")[10].get_text())[:5]
            self.tasa_independiente_cuprum = clear_string(letters[7].select("strong")[13].get_text())
            self.tasa_independiente_habitat = clear_string(letters[7].select("strong")[16].get_text())
            self.tasa_independiente_planvital = clear_string(letters[7].select("strong")[19].get_text())
            self.tasa_independiente_provida = clear_string(letters[7].select("strong")[22].get_text())
            self.tasa_independiente_modelo = clear_string(letters[7].select("strong")[25].get_text())

        except ValueError:
            return ""
