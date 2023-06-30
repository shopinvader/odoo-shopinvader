# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import uuid

from odoo import api, fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    uuid = fields.Char(string="EShop Unique identifier", readonly=True)

    @api.model
    def _get_open_cart_domain(self, partner_id, uuid=None):
        domain = [
            ("typology", "=", "cart"),
            ("state", "=", "draft"),
            ("partner_id", "=", partner_id),
        ]
        if uuid:
            domain.append(("uuid", "=", uuid))
        return domain

    @api.model
    def _find_open_cart(self, partner_id=None, uuid=None):
        """
        Try to find a cart for the given partner_id and uuid.
        If no cart is found, try to find another cart for the given partner.
        """
        if not partner_id:
            # Cannot return a cart if partner is not given
            return self.browse()
        domain = self._get_open_cart_domain(partner_id, uuid=uuid)
        cart = self.search(domain, limit=1)
        if not cart and uuid:
            # maybe a current cart exists with another uuid
            domain = self._get_open_cart_domain(partner_id, uuid=None)
            cart = self.search(domain, limit=1)
        return cart

    @api.model
    def _get_default_pricelist_id(self):
        """Return the pricelist to use if no one found on the partner
        By default, we return the one defined on the public user (inactive by default).
        """
        return (
            self.env.ref("base.public_user")
            .partner_id.with_context(active_test=False)
            .property_product_pricelist.id
        )

    @api.model
    def _play_onchanges_cart(self, vals):
        """
        Play all onchanges bypassing the rules
        """
        return self.sudo().play_onchanges(vals, vals.keys())

    @api.model
    def _prepare_cart(self, partner_id):
        vals = {
            "uuid": str(uuid.uuid4()),
            "typology": "cart",
            "partner_id": partner_id,
        }
        vals.update(self._play_onchanges_cart(vals))
        if not vals.get("pricelist_id"):
            vals["pricelist_id"] = self._get_default_pricelist_id()
        return vals

    @api.model
    def _create_empty_cart(self, partner_id):
        """Create a new empty cart for a given partner"""
        vals = self._prepare_cart(partner_id)
        return self.create(vals)

    def _get_cart_line(self, product_id):
        """
        Return the sale order line of the cart associated to the given product.
        """
        self.ensure_one()
        return self.order_line.filtered(
            lambda l, product_id=product_id: l.product_id.id == product_id
        )[:1]
