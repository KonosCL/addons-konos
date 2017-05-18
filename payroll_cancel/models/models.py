# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.multi
    def delete_done_sheet(self):
        for rec in self:
            if not rec.journal_id.update_posted:
                raise exceptions.UserError("Primero deberia Permitir cancelación de asientos para este diario.")
            else:
                if rec.move_id:
                    rec.move_id.button_cancel()
                    rec.move_id.unlink()
                rec.state = 'draft'
                rec.unlink()

