import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, installed_version):
    _logger.warning("Post Migrating l10n_cl_chart_of_account from version %s to 14.0.1.13.3" % installed_version)

    env = api.Environment(cr, SUPERUSER_ID, {})
    account_id = env.ref('l10n_cl_chart_of_account.210701').id
    for r in env["account.tax.repartition.line"].sudo().search([
            ("sii_type", "!=", 'R'),
            ("account_id.code", "=", '210709'),
        ]):
        r.account_id = account_id

    account_id = env.ref('l10n_cl_chart_of_account.110701').id
    for r in env["account.tax.repartition.line"].sudo().search([
            ("sii_type", "!=", 'R'),
            ("account_id.code", "=", '110708'),
        ]):
        r.account_id = account_id

    cr.execute('''UPDATE account_move_line aml
                SET account_id = rl.account_id
                FROM account_tax_repartition_line rl
                    JOIN account_tax t ON t.id=rl.refund_tax_id OR t.id=rl.invoice_tax_id
                    WHERE t.id = tax_line_id
                        AND aml.account_id != rl.account_id
                        AND aml.tax_line_id IS NOT NULL
                        AND (rl.sii_type != 'R' OR rl.sii_type is null)
                ''')
