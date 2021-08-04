# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def _fix_multicompany_ir_rules(env):
    """Fix Multi-Company ir.rules

    These rules are set as noupdate=1, but they weren't migrated properly
    as they don't account for multiple companies set in context.
    """
    refs = [
        "shopinvader_backend_comp_rule",
        "shopinvader_category_comp_rule",
        "shopinvader_partner_comp_rule",
        "shopinvader_product_comp_rule",
        "shopinvader_variant_comp_rule",
    ]
    for ref in refs:
        xmlid = "shopinvader.{}".format(ref)
        rule = env.ref(xmlid, raise_if_not_found=False)
        if not rule:
            continue
        rule.domain_force = """
            [
                '|',
                ('company_id', '=', False),
                ('company_id', 'in', company_ids),
            ]
        """


def migrate(cr, version):
    if not version:
        return
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        _fix_multicompany_ir_rules(env)
