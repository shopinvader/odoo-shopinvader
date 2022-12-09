# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = ["base.shopinvader.service", "sale.cart.service"]
    _name = "shopinvader.sale.cart.service"
    _usage = "cart"
    _collection = "shopinvader.api.v2"

    @property
    def anonymous_partner(self):
        return self.shopinvader_backend.anonymous_partner_id

    def _get_open_cart_domain(self, uuid=None):
        domain = super(CartService, self)._get_open_cart_domain(uuid=uuid)
        domain.append(("shopinvader_backend_id", "=", self.shopinvader_backend.id))
        return domain

    def _prepare_cart(self):
        vals = super(CartService, self)._prepare_cart()
        vals["shopinvader_backend_id"] = self.shopinvader_backend.id
        if self.shopinvader_backend.sequence_id:
            vals["name"] = self.shopinvader_backend.sequence_id._next()
        if self.shopinvader_backend.account_analytic_id.id:
            vals["project_id"] = self.shopinvader_backend.account_analytic_id.id
        if self.shopinvader_backend.pricelist_id:
            # We must always force the pricelist. In the case of sale_profile
            # the pricelist is not set on the backend
            vals.update({"pricelist_id": self.shopinvader_backend.pricelist_id.id})
        return vals

    def _get_default_pricelist_id(self):
        return self.shopinvader_backend.pricelist_id.id

    def _convert_cart_to_json(self, sale):
        vals = super(CartService, self)._convert_cart_to_json(sale)
        vals.update(
            {
                "state_label": self._get_selection_label(sale, "shopinvader_state"),
                "state": sale.shopinvader_state,
            }
        )
        return vals
