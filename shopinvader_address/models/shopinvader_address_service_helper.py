# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import MissingError, UserError

from odoo.addons.base.models.res_partner import Partner as ResPartner


class ShopinvaderAddressServiceHelper(models.Model):
    _name = "shopinvader_address.service.helper"
    _description = "Shopinvader Address Service Helper"

    def _ensure_billing_address_not_used(self, address) -> None:
        """
        Check if Billing Address is used on confirmed sale order
        """
        address.ensure_one()
        sale_order = (
            self.env["sale.order"]
            .sudo()
            .search(
                [
                    ("partner_invoice_id", "=", address.id),
                    ("state", "in", ("done", "sale")),
                ],
                limit=1,
            )
        )
        if len(sale_order) > 0:
            raise UserError(
                _(
                    "Can not update billing addresses(%(address_id)d)"
                    "because it is already used on confirmed sale order",
                    address_id=address.id,
                )
            )

    def _ensure_shipping_address_not_used(self, address) -> None:
        """
        Check if Shipping Address is used on confirmed sale order
        """
        address.ensure_one()
        sale_order = (
            self.env["sale.order"]
            .sudo()
            .search(
                [
                    ("partner_shipping_id", "=", address.id),
                    ("state", "in", ("done", "sale")),
                ],
                limit=1,
            )
        )
        if len(sale_order) > 0:
            raise UserError(
                _(
                    "Can not delete Shipping address(%(address_id)d)"
                    "because it is already used on confirmed sale order",
                    address_id=address.id,
                )
            )

    # --- Billing ---
    # Billing address is unique and corresponds to authenticated_partner

    def _get_billing_addresses(self, partner) -> "ResPartner":
        partner.ensure_one()
        return partner

    def _get_billing_address(self, partner, address_id: int) -> "ResPartner":
        partner.ensure_one()
        addresses = self._get_billing_addresses(partner)
        address = addresses.filtered(lambda rec: rec.id == address_id)
        if not address:
            raise MissingError(
                _(
                    "Billing address not found, id: %(address_id)d",
                    address_id=address_id,
                )
            )
        return address

    def _create_billing_address(self, partner, vals: dict) -> "ResPartner":
        raise UserError(_("Creation of billing addresses is not supported"))

    def _update_billing_address(
        self, partner, vals: dict, address_id: int
    ) -> "ResPartner":
        partner.ensure_one()
        address = self._get_billing_address(partner, address_id)

        # if billing address is already used, it is not possible to modify it
        # an error will be raised
        self._ensure_billing_address_not_used(address)

        address.write(vals)

        return address

    # ---Shipping ---

    def _get_shipping_addresses(self, partner) -> "ResPartner":
        partner.ensure_one()
        domain = [("type", "=", "delivery"), ("parent_id", "=", partner.id)]

        return self.env["res.partner"].search(domain)

    def _get_shipping_address(self, partner, address_id: int) -> "ResPartner":
        partner.ensure_one()

        addresses = self._get_shipping_addresses(partner)
        address = addresses.filtered(lambda rec: rec.id == address_id)
        if not address:
            raise MissingError(
                _(
                    "Shipping address not found, id: %(address_id)d",
                    address_id=address_id,
                )
            )

        return address

    def _create_shipping_address(self, partner, vals: dict) -> "ResPartner":
        partner.ensure_one()
        vals = dict(vals, parent_id=partner.id, type="delivery")
        return self.env["res.partner"].create(vals)

    def _update_shipping_address(
        self, partner, vals: dict, address_id: int
    ) -> "ResPartner":

        if any(key in vals for key in ("parent_id", "type")):
            raise UserError(
                _(
                    "parent_id and type cannot be modified on"
                    " shopinvader shipping address, id: %(address_id)d",
                    address_id=address_id,
                )
            )

        partner.ensure_one()
        address = self._get_shipping_address(partner, address_id)

        # if shipping address is already used, it is not possible to modify it
        self._ensure_shipping_address_not_used(address)

        # update_address
        address.write(vals)
        return address

    def _delete_shipping_address(self, partner, address_id: int) -> None:
        """
        Delete of shopinvader shipping addresses will result to an archive
        """
        address = self._get_shipping_address(partner, address_id)
        if address:
            self._ensure_shipping_address_not_used(address)

            # archive address
            address.active = False
        else:
            raise MissingError(
                _("No address found, id: %(address_id)d", address_id=address_id)
            )
