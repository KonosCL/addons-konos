Módulo que permite seleccionar si queremos facturar una venta en la moneda de la cotización o la moneda local. 
Esto se usa en Chile para cotizar en UF, USD y Facturar en Pesos. 
 
https://youtu.be/TLgGE-veWh4

Para poder configurar hay que tener en cuenta lo siguiente:

a. Moneda Principal CLP

b. Instalar Financial Indicators Preferiblemente

c. Colocar el Token del SBIF

d. Quitar el Update Rate Currency de Odoo

e. Colocar Precisión Decimal

f. Currency Rate 14

g. Currency 14

h. Instalar Sale Order Currency

i. Colocar Redondeo Global

j. Factor Redondeo CLP = 1

k. Activar el Cron Job Update Chilean Financial Indicators para que actualice la tasas a las 9 am. 

