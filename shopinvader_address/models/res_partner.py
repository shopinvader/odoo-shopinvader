# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import MissingError, UserError


class ResPartner(models.Model):

    _inherit = "res.partner"

    def _shopinvader_billing_addresses_already_used(self):
        """
        Check if Address is used on confirmed sale order
        """
        self.ensure_one()
        move_id = (
            self.env["sale.order"]
            .sudo()
            .search(
                [
                    ("partner_invoice_id", "=", self.id),
                    ("state", "in", ("done", "sale")),
                ],
                limit=1,
            )
        )
        return len(move_id) > 0

    # --- Billing ---
    # Billing addresses is unique and corresponds to authenticated_partner

    def _get_shopinvader_billing_address(self) -> "ResPartner":
        self.ensure_one()
        return self

    def _update_shopinvader_billing_address(self, vals: dict) -> "ResPartner":
        self.ensure_one()
        # if billing addresses is already used, it is not possible to modify it
        if self._shopinvader_billing_addresses_already_used():
            raise UserError(
                _(
                    "Can not update billing addresses(%(address_id)d)"
                    "because it is already used on billings",
                    address_id=self.id,
                )
            )

        self.write(vals)

        return self

    # ---Shipping ---

    def _get_shopinvader_shipping_addresses(
        self, address_id: int = None
    ) -> "ResPartner":
        self.ensure_one()
        domain = [("type", "=", "delivery"), ("parent_id", "=", self.id)]

        if address_id is not None:
            domain.append(("id", "=", address_id))

        return self.env["res.partner"].search(domain)

    def _create_shopinvader_shipping_address(self, vals: dict) -> "ResPartner":
        self.ensure_one()
        vals.update(
            {
                "parent_id": self.id,
                "type": "delivery",
            }
        )
        return self.env["res.partner"].create(vals)

    def _update_shopinvader_shipping_address(
        self, vals: dict, address_id: int
    ) -> "ResPartner":

        if any(key in vals for key in ("parent_id", "type")):
            raise UserError(
                _(
                    "parent_id and type cannot be modified on"
                    " shopinvader shipping address, id: %(address_id)d",
                    address_id=address_id,
                )
            )

        self.ensure_one()
        addresses = self._get_shopinvader_shipping_addresses(address_id)
        if not addresses:
            raise MissingError(
                _("No address found, id: %(address_id)d", address_id=address_id)
            )

        # update_address
        addresses.write(vals)
        return addresses

    def _delete_shopinvader_shipping_address(self, address_id: int) -> None:
        """
        Delete of shopinvader shipping addresses will result to an archive
        """
        addresses = self._get_shopinvader_shipping_addresses(address_id)
        if addresses:
            # archive address
            addresses.active = False
        else:
            raise MissingError(
                _("No address found, id: %(address_id)d", address_id=address_id)
            )
