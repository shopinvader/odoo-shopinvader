# Copyright 2021 Camptocamp (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.component.core import Component


class CustomerService(Component):
    _inherit = "shopinvader.customer.service"

    def _to_customer_info(self, partner):
        res = super()._to_customer_info(partner)
        if self.shopinvader_backend.use_sale_profile:
            invader_partner = partner._get_invader_partner(self.shopinvader_backend)
            res["sale_profile"] = invader_partner.sale_profile_id.code
        return res
