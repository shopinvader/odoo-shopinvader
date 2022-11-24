# Copyright 2022 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, api


def _upgrade_shopinvader_model_access(env):
    """
    Upgrade the "shopinvader partner binding edit" access rights
    (as it's not update)
    """
    sec_group = env.ref("shopinvader.group_shopinvader_partner_binding")
    env.ref("shopinvader.access_shopinvader_partner_edit").write(
        {
            "group_id": sec_group.id,
        }
    )


def migrate(cr, version):
    if not version:
        return
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        _upgrade_shopinvader_model_access(env)
