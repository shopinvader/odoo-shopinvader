# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import MissingError, UserError


class ResPartner(models.Model):

    _inherit = "res.partner"

    def _shopinvader_billing_address_already_used(self):
        """
        Check if Billing Address is used on confirmed sale order
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

    def _shopinvader_shipping_address_already_used(self):
        """
        Check if Shipping Address is used on confirmed sale order
        """
        self.ensure_one()
        move_id = (
            self.env["sale.order"]
            .sudo()
            .search(
                [
                    ("partner_shipping_id", "=", self.id),
                    ("state", "in", ("done", "sale")),
                ],
                limit=1,
            )
        )
        return len(move_id) > 0

    # --- Billing ---
    # Billing addresses is unique and corresponds to authenticated_partner

    def _get_shopinvader_billing_addresses(self) -> "ResPartner":
        self.ensure_one()
        return self

    def _create_shopinvader_billing_address(self, vals: dict) -> "ResPartner":
        raise UserError(_("Creation of billing addresses is not supported"))

    def _update_shopinvader_billing_address(
        self, vals: dict, address_id: int
    ) -> "ResPartner":
        self.ensure_one()

        if address_id != self.id:
            raise UserError(
                _(
                    "Can not update billing addresses(%(address_id)d)"
                    "because it doesn't correspond to authenticated partner's billing address",
                    address_id=self.id,
                )
            )

        # if billing addresses is already used, it is not possible to modify it
        if self._shopinvader_billing_address_already_used():
            raise UserError(
                _(
                    "Can not update billing addresses(%(address_id)d)"
                    "because it is already used on confirmed sale order",
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
        address = self._get_shopinvader_shipping_addresses(address_id)
        if not address:
            raise MissingError(
                _("No address found, id: %(address_id)d", address_id=address_id)
            )

        # if shipping addresses is already used, it is not possible to modify it
        if address._shopinvader_shipping_address_already_used():
            raise UserError(
                _(
                    "Can not update Shipping address(%(address_id)d)"
                    "because it is already used on confirmed sale order",
                    address_id=self.id,
                )
            )

        # update_address
        address.write(vals)
        return address

    def _delete_shopinvader_shipping_address(self, address_id: int) -> None:
        """
        Delete of shopinvader shipping addresses will result to an archive
        """
        address = self._get_shopinvader_shipping_addresses(address_id)
        if address:
            if address._shopinvader_shipping_address_already_used():
                raise UserError(
                    _(
                        "Can not delete Shipping address(%(address_id)d)"
                        "because it is already used on confirmed sale order",
                        address_id=self.id,
                    )
                )
            # archive address
            address.active = False
        else:
            raise MissingError(
                _("No address found, id: %(address_id)d", address_id=address_id)
            )
