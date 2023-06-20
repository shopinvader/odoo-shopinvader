# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from ..schema.schema import AddressSearch


class ResPartner(models.Model):

    _inherit = "res.partner"

    shopinvader_partner_ids = fields.One2many(
        comodel_name="res.partner",
        inverse_name="shopinvader_main_partner_id",
        string="Shopinvader Addresses",
    )

    shopinvader_main_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Authenticated partner address",
    )

    @api.model
    def _build_shopinvader_address_domain(self, query) -> list:
        domain = []

        if query.name is not None:
            domain.append(("name", "ilike", query.name))
        if query.street is not None:
            domain.append(("street", "ilike", query.name))
        if query.street2 is not None:
            domain.append(("street2", "ilike", query.name))
        if query.zip is not None:
            domain.append(("zip", "ilike", query.name))
        if query.city is not None:
            domain.append(("city", "ilike", query.name))
        if query.phone is not None:
            domain.append(("phone", "ilike", query.name))
        if query.email is not None:
            domain.append(("email", "ilike", query.name))

        # search on state/country is performed
        # on name or code of state/country
        if query.state is not None:
            domain.join(
                [
                    "|",
                    ("state_id.name", "ilike", query.state),
                    ("state_id.code", "ilike", query.state),
                ]
            )
        if query.country is not None:
            domain.join(
                [
                    "|",
                    ("country.name", "ilike", query.country),
                    ("country.code", "ilike", query.country),
                ]
            )

        return domain

    @api.model
    def _search_shopinvader_address(self, query: AddressSearch, limit, offset):
        """
        search using query
        """
        domain = self._build_shopinvader_address_domain(query)
        return self.env["res.partner"].search(domain, limit=limit, offset=offset)

    @api.model
    def _create_vals_shopinvader_address(self, data) -> dict:
        state_id = self.env["res.country.state"].search(
            [
                "|",
                ("name", "=", data.state),
                ("code", "=", data.state),
            ],
            limit=1,
        )

        country_id = self.env["res.country"].search(
            [
                "|",
                ("name", "=", data.country),
                ("code", "=", data.country),
            ]
        )

        vals = {
            "name": data.name,
            "street": data.street,
            "street2": data.street2 or "",
            "zip": data.zip,
            "city": data.city,
            "phone": data.phone or "",
            "email": data.email or "",
            "state_id": state_id.id,
            "country_id": country_id.id,
            "shopinvader_main_partner_id": self.env.context.get(
                "authenticated_partner_id"
            ),
        }
        return vals

    @api.model
    def _create_shopinvader_address(self, data) -> "ResPartner":
        vals = self._create_vals_shopinvader_address(data)
        return self.env["res.partner"].sudo().create(vals)
