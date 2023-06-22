# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import MissingError, UserError


class ResPartner(models.Model):

    _inherit = "res.partner"

    def _shopinvader_billing_addresses_already_used(self):
        self.ensure_one()
        move_id = (
            self.env["account.move"]
            .sudo()
            .search([("commercial_partner_id", "=", self.id)], limit=1)
        )
        return len(move_id) > 0

    #### Billing ####
    # Billing addresses is unique and corresponds to authenticated_partner

    def _get_shopinvader_billing_addresses(
        self
    ) -> "ResPartner":
        self.ensure_one()
        return self

    def _update_shopinvader_billing_addresses(
        self, vals: dict
    ) -> "ResPartner":
        self.ensure_one()
        # if billing addresses is already used, it is not possible to modify it
        if self._shopinvader_billing_addresses_already_used():
            raise UserError(
                _(
                    "Can not update billing addresses because it is already used on billings"
                )
            )

        self.write(vals)

        return self

    #### Shipping ####

    def _get_shopinvader_shipping_addresses(
        self, rec_id: int = None
    ) -> "ResPartner":
        self.ensure_one()
        domain = [("type", "=", "delivery"),("parent_id","=",self.id)]

        if rec_id is not None:
            domain.append(("id", "=", rec_id))

        addresses = self.env["res.partner"].search(domain)

        return addresses


    def _create_shopinvader_shipping_addresses(
        self, vals: dict
    ) -> "ResPartner":
        self.ensure_one()
        vals.update(
            {
                "parent_id": self.id,
                "type": "delivery",
            }
        )
        return self.env["res.partner"].create(vals)

    @api.model
    def _update_shopinvader_shipping_addresses(
        self, vals: dict, rec_id: int
    ) -> "ResPartner":
        self.ensure_one()
        addresses = self._get_shopinvader_shipping_addresses(rec_id)
        if not addresses:
            raise MissingError(_("No address found"))
        # update_address
        addresses.write(vals)
        return addresses

    @api.model
    def _delete_shopinvader_shipping_addresses(self, rec_id: int) -> None:
        addresses = self._get_shopinvader_shipping_addresses(rec_id)
        if addresses:
            # archive address
            addresses.active = False
