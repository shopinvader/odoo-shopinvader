# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    def _prepare_cart(self):
        vals = super(CartService, self)._prepare_cart()
        backend = self.shopinvader_backend
        partner = self.partner or self.shopinvader_backend.anonymous_partner_id
        if backend.use_sale_profile:
            partner_pricelist = partner.property_product_pricelist
            if partner_pricelist not in backend.sale_profile_ids.mapped("pricelist_id"):
                vals.update(
                    {
                        "pricelist_id": backend.sale_profile_ids.filtered(
                            "default"
                        ).pricelist_id.id
                    }
                )
        return vals
