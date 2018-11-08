#-------------------------------------------------------------
#SPANISH
#-------------------------------------------------------------
from odoo.tools.translate import _

units_29 = ( 'CERO', 'UN', 'DOS', 'TRES', 'CUATRO', 'CINCO', 'SEIS',
          'SIETE', 'OCHO', 'NUEVE', 'DIEZ', 'ONCE', 'DOCE',
          'TRECE', 'CATORCE', 'QUINCE', 'DIECISÉIS', 'DIECISIETE', 'DIECIOCHO',
          'DIECINUEVE', 'VEINTE', 'VEINTIÚN', 'VEINTIDÓS', 'VEINTITRÉS', 'VEINTICUATRO',
          'VEINTICINCO', 'VEINTISÉIS', 'VEINTISIETE', 'VEINTIOCHO', 'VEINTINUEVE' )

tens = ( 'TREINTA', 'CUARENTA', 'CINCUENTA', 'SESENTA', 'SETENTA', 'OCHENTA', 'NOVENTA', 'CIEN')

# La numeración comentada es anglosajona, donde un billón son mil millones. Sin embargo, en la española
# el billón es un millón de millones.
#denom = ( '',
#          'MIL', 'MILLÓN', 'Billón', 'Trillón', 'Cuatrillón', 'Quintillón',  'Sextillón',
#          'Septillón', 'Octillón', 'Nonillón', 'Decillón', 'Undecillón', 'Dodecillón',  'Tredecillón',
#          'Cuatridecillón', 'Quindecillón', 'Sexdecillón', 'Septidecillón', 'Octodecillón',
#          'Nonidecillón', 'Vigillón' )
#denom_plural = ( '',
#          'Mil', 'Millones', 'Billones', 'Trillones', 'Cuatrillones', 'Quintillones',  'Sextillones',
#          'Septillones', 'Octillones', 'Nonillones', 'Decillones', 'Undecillones', 'Dodecillones',  'Tredecillones',
#          'Cuatridecillones', 'Quindecillones', 'Sexdecillones', 'Septidecillones', 'Octodecillones',
#          'Nonidecillones', 'Vigillones' )

denom = ('',
          'MIL', 'MILLÓN', 'MIL MILLONES', 'BILLÓN', 'MIL BILLONES', 'TRILLÓN', 'MIL TRILLONES',
          'CUATRILLÓN', 'MIL CUATRILLONES', 'QUINTILLÓN', 'MIL QUINTILLONES', 'SEXTILLÓN', 'MIL SEXTILLONES', 'SEPTILLÓN',
          'MIL SEPTILLONES', 'OCTILLÓN', 'MIL OCTILLONES', 'NONILLÓN', 'MIL NONILLONES', 'DECILLÓN', 'MIL DECILLONES' )

denom_plural = ('',
          'MIL', 'MILLONES', 'MIL MILLONES', 'BILLONES', 'MIL BILLONES', 'TRILLONES', 'MIL TRILLONES',
          'CUATRILLONES', 'MIL CUATRILLONES', 'QUINTILLONES', 'MIL QUINTILLONES', 'SEXTILLONES', 'MIL SEXTILLONES', 'SEPTILLONES',
          'MIL SEPTILLONES', 'OCTILLONES', 'MIL OCTILLONES', 'NONILLONES', 'MIL NONILLONES', 'DECILLONES', 'MIL DECILLONES' )

# convertir valores inferiores a 100 a texto español.
def _convert_nn(val):
    if val < 30:
        return units_29[val]
    for (dcap, dval) in ((k, 30 + (10 * v)) for (v, k) in enumerate(tens)):
        if dval + 10 > val:
            if val % 10:
                return dcap + ' Y ' + units_29[val % 10]
            return dcap

# convertir valores inferiores a 1000 a texto español.
def _convert_nnn(val):
    word = ''
    (mod, quotient) = (val % 100, val // 100)
    if quotient > 0:
        if quotient == 1:
            if mod == 0:
                word = 'CIEN'
            else:
                word = 'CIENTO'
        elif quotient == 5:
                word = 'QUINIENTOS'
        elif quotient == 9:
            word = 'NOVECIENTOS'
        else:
            word = units_29[quotient] + 'CIENTOS'
        if mod > 0:
            word = word + ' '
    if mod > 0:
        word = word + _convert_nn(mod)
    return word

def spanish_number(val):
    if val < 100:
        return _convert_nn(val)
    if val < 1000:
        return _convert_nnn(val)
    #valores a partir de mil
    for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(denom))):
        if dval > val:
            mod = 1000 ** didx
            l = val // mod
            r = val - (l * mod)

            # Varios casos especiales:
            # Si l==1 y didx==1 (caso concreto del "mil"), no queremos que diga "un mil", sino "mil".
            # Si se trata de un millón y órdenes superiores (didx>0), sí queremos el "un".
            # Si l > 1 no queremos que diga "cinco millón", sino "cinco millones".
            if l == 1:
                if didx == 1:
                    ret = denom[didx]
                else:
                    ret = _convert_nnn(l) + ' ' + denom[didx]
            else:
                ret = _convert_nnn(l) + ' ' + denom_plural[didx]

            if r > 0:
                ret = ret + ' ' + spanish_number(r)
            return ret

def amount_to_text_es(number, currency):
    number = '%.2f' % number
    # Nota: el nombre de la moneda viene dado en el informe como "euro". Aquí se convierte a
    # uppercase y se pone en plural añadiendo una "s" al final del nombre. Esto no cubre todas
    # las posibilidades (nombres compuestos de moneda), pero sirve para las más comunes.
    units_name = currency.upper()
    int_part, dec_part = str(number).split('.')
    start_word = spanish_number(int(int_part))
    end_word = spanish_number(int(dec_part))
    cents_number = int(dec_part)
    cents_name = (cents_number > 1) and 'CÉNTIMOS' or 'CÉNTIMO'
    final_result = start_word +' ' + units_name

    # Añadimos la "s" de plural al nombre de la moneda si la parte entera NO es UN euro
    if int(int_part) != 1:
        final_result += 'S'

    if int(dec_part) > 0:
        final_result += ' CON ' + end_word +' '+cents_name
    return final_result


#-------------------------------------------------------------
# Generic functions
#-------------------------------------------------------------

_translate_funcs = {'es' : amount_to_text_es}

def amount_to_text(nbr, lang='es', currency='euros'):
    """
    Converts an integer to its textual representation, using the language set in the context if any.
    Example:
        1654: thousands six cent cinquante-quatre.
    """
    if not _translate_funcs.has_key(lang):
        print ("WARNING: no translation function found for lang: '%s'" % (lang,))
        lang = 'es'
    return _translate_funcs[lang](abs(nbr), currency)

#if __name__=='__main__':
#    from sys import argv
#
#    lang = 'nl'
#    if len(argv) < 2:
#        for i in range(1,200):
#            print i, ">>", amount_to_text(i, lang)
#        for i in range(200,999999,139):
#            print i, ">>", amount_to_text(i, lang)
#    else:
#        print amount_to_text(int(argv[1]), lang)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
