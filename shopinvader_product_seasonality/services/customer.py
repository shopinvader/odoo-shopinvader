# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class CustomerService(Component):
    _inherit = "shopinvader.customer.service"

    def _to_customer_info(self, partner):
        res = super()._to_customer_info(partner)
        config = self._get_seasonal_config_id(partner)
        res["seasonal_config_id"] = config.id
        return res

    # TODO: this should probably go into the sale module
    def _get_seasonal_config_id(self, partner):
        commercial_partner = partner.commercial_partner_id
        return partner.seasonal_config_id or commercial_partner.seasonal_config_id
