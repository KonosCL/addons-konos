#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero
from odoo.tools.translate import _




class HrPayslipAnalytic(models.Model):
    _inherit = 'hr.payslip'
    
    @api.multi
    def _prepare_analytic_account(self, line):
        cost_center = super(HrPayslipAnalytic, self)._prepare_analytic_account(line)
        if line.salary_rule_id.account_analytic_true:
            cost_center = self.contract_id.analytic_account_id.id
        return cost_center


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'
    
    account_analytic_true = fields.Boolean('Analytic Account in Contract?')
