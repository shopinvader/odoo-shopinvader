# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import MissingError, UserError


class ResPartner(models.Model):

    _inherit = "res.partner"

    def _ensure_shopinvader_invoicing_address_not_used(self) -> None:
        """
        Check if Invoicing Address is used on confirmed sale order
        """
        self.ensure_one()
        sale_order = (
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
        if len(sale_order) > 0:
            raise UserError(
                _(
                    "Can not update invoicing addresses(%(address_id)d)"
                    "because it is already used on confirmed sale order",
                    address_id=self.id,
                )
            )

    def _ensure_shopinvader_delivery_address_not_used(self) -> None:
        """
        Check if Delivery Address is used on confirmed sale order
        """
        self.ensure_one()
        sale_order = (
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
        if len(sale_order) > 0:
            raise UserError(
                _(
                    "Can not delete Delivery address(%(address_id)d)"
                    "because it is already used on confirmed sale order",
                    address_id=self.id,
                )
            )

    # --- Invoicing ---
    # Invoicing address is unique and corresponds to authenticated_partner

    def _get_shopinvader_invoicing_addresses(self) -> "ResPartner":
        self.ensure_one()
        return self

    def _get_shopinvader_invoicing_address(self, address_id: int) -> "ResPartner":
        self.ensure_one()
        addresses = self._get_shopinvader_invoicing_addresses()
        address = addresses.filtered(lambda rec: rec.id == address_id)
        if not address:
            raise MissingError(
                _(
                    "Invoicing address not found, id: %(address_id)d",
                    address_id=address_id,
                )
            )
        return address

    def _create_shopinvader_invoicing_address(self, vals: dict) -> "ResPartner":
        raise UserError(_("Creation of invoicing addresses is not supported"))

    def _update_shopinvader_invoicing_address(
        self, vals: dict, address_id: int
    ) -> "ResPartner":
        self.ensure_one()
        address = self._get_shopinvader_invoicing_address(address_id)

        # if invoicing address is already used, it is not possible to modify it
        # an error will be raised
        address._ensure_shopinvader_invoicing_address_not_used()

        address.write(vals)

        return address

    # ---Delivery ---

    def _get_shopinvader_delivery_addresses(self) -> "ResPartner":
        self.ensure_one()
        domain = [("type", "=", "delivery"), ("parent_id", "=", self.id)]

        return self.env["res.partner"].search(domain)

    def _get_shopinvader_delivery_address(self, address_id: int) -> "ResPartner":
        self.ensure_one()

        addresses = self._get_shopinvader_delivery_addresses()
        address = addresses.filtered(lambda rec: rec.id == address_id)
        if not address:
            raise MissingError(
                _(
                    "Delivery address not found, id: %(address_id)d",
                    address_id=address_id,
                )
            )

        return address

    def _create_shopinvader_delivery_address(self, vals: dict) -> "ResPartner":
        self.ensure_one()
        vals = dict(vals, parent_id=self.id, type="delivery")
        return self.env["res.partner"].create(vals)

    def _update_shopinvader_delivery_address(
        self, vals: dict, address_id: int
    ) -> "ResPartner":

        if any(key in vals for key in ("parent_id", "type")):
            raise UserError(
                _(
                    "parent_id and type cannot be modified on"
                    " shopinvader delivery address, id: %(address_id)d",
                    address_id=address_id,
                )
            )

        self.ensure_one()
        address = self._get_shopinvader_delivery_address(address_id)

        # if delivery address is already used, it is not possible to modify it
        address._ensure_shopinvader_delivery_address_not_used()

        # update_address
        address.write(vals)
        return address

    def _delete_shopinvader_delivery_address(self, address_id: int) -> None:
        """
        Delete of shopinvader delivery addresses will result to an archive
        """
        address = self._get_shopinvader_delivery_address(address_id)
        if address:
            address._ensure_shopinvader_delivery_address_not_used()

            # archive address
            address.active = False
        else:
            raise MissingError(
                _("No address found, id: %(address_id)d", address_id=address_id)
            )
