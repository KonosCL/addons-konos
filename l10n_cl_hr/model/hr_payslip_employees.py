from odoo import api, fields, models, tools, _


class hr_payslip_employees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    @api.multi
    def compute_sheet(self):
        indicadores_id = False
        if self.env.context.get('active_id'):
            indicadores_id = self.env['hr.payslip.run'].browse(self.env.context.get('active_id')).indicadores_id.id
        return super(hr_payslip_employees, self.with_context(indicadores_id=indicadores_id)).compute_sheet()

