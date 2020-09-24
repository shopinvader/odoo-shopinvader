# Copyright 2019 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.controllers import main


class InvaderController(main.InvaderController):
    def _get_component_context(self):
        res = super(InvaderController, self)._get_component_context()
        if res["partner"] and res["partner"].is_invader_user:
            # just a user of the same main account:
            # override partner w/ its parent
            # The original partner is already into `res['partner_user']`
            res["partner"] = res["partner"].parent_id
        return res
