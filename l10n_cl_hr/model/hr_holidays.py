
import math
from odoo import api, fields, models, tools


class HRHolidaysStatus(models.Model):
    _inherit = 'hr.leave.type'
    is_continued = fields.Boolean('Disccount Weekends')


class HRHolidays(models.Model):
    _inherit = 'hr.leave'

    def _get_number_of_days(self, date_from, date_to, employee_id):
        #En el caso de las licencias descontamos dias corridos
        if employee_id and self.holiday_status_id.is_continued:
            time_delta = date_to - date_from
            return math.ceil(time_delta.days + float(time_delta.seconds) / 86400)
        else:
            return super(HRHolidays, self)._get_number_of_days(date_from, date_to, employee_id)
