# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
import math
from datetime import datetime, timedelta
from odoo import api, fields, models, tools
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF

HOURS_PER_DAY = 8

class HRHolidaysStatus(models.Model):
    _inherit = 'hr.holidays.status'
    is_continued = fields.Boolean('Disccount Weekends')


class HRHolidays(models.Model):
    _inherit = 'hr.holidays'


    def _get_number_of_days(self, date_from, date_to, employee_id):
        from_dt = fields.Datetime.from_string(date_from)
        to_dt = fields.Datetime.from_string(date_to)

        #Función Original: Agregamos la opción de días contínuos para licencias dias corridos
        if employee_id and self.holiday_status_id.is_continued:
            time_delta = to_dt - from_dt
            return math.ceil(time_delta.days + float(time_delta.seconds) / 86400)
        elif employee_id:
            employee = self.env['hr.employee'].browse(employee_id)
            return employee.get_work_days_count(from_dt, to_dt)
        time_delta = to_dt - from_dt
        return math.ceil(time_delta.days + float(time_delta.seconds) / 86400)


    #Función Original: Agregamos el recálculo al cambiar holiday_status_id
    @api.multi
    @api.depends('number_of_days_temp', 'type', 'holiday_status_id')
    def _compute_number_of_days(self):
        for holiday in self:
            if holiday.type == 'remove':
                holiday.number_of_days = -holiday.number_of_days_temp
            else:
                holiday.number_of_days = holiday.number_of_days_temp




    #Función Original: Agregamos el recálculo al cambiar holiday_status_id
    @api.onchange('date_from','holiday_status_id','employee_id')
    def _onchange_date_from(self):
        """ If there are no date set for date_to, automatically set one 8 hours later than
            the date_from. Also update the number_of_days.
        """
        date_from = self.date_from
        date_to = self.date_to

        # No date_to set so far: automatically compute one 8 hours later
        if date_from and not date_to:
            date_to_with_delta = fields.Datetime.from_string(date_from) + timedelta(hours=HOURS_PER_DAY)
            self.date_to = str(date_to_with_delta)

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            self.number_of_days_temp = self._get_number_of_days(date_from, date_to, self.employee_id.id)
        else:
            self.number_of_days_temp = 0


    #Función Original: Agregamos el recálculo al cambiar holiday_status_id
    @api.onchange('date_to','holiday_status_id','employee_id')
    def _onchange_date_to(self):
        """ Update the number_of_days. """
        date_from = self.date_from
        date_to = self.date_to

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            self.number_of_days_temp = self._get_number_of_days(date_from, date_to, self.employee_id.id)
        else:
            self.number_of_days_temp = 0