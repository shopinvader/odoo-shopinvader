# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, exceptions, fields, models


class ShopinvaderSaleProfile(models.Model):
    """Represent a customer sale profile with a specific pricelist  per backend."""

    _name = "shopinvader.sale.profile"
    _description = "Shopinvader Customer profile"
    _rec_name = "code"

    backend_id = fields.Many2one(
        "shopinvader.backend", "Backend", required=True, index=True
    )
    pricelist_id = fields.Many2one(
        "product.pricelist",
        "Pricelist",
        help="Pricelist used for the sale profile",
    )
    fiscal_position_ids = fields.Many2many(
        "account.fiscal.position",
        "shopinvader_sale_profile_fiscal_position_rel",
        "shopinvader_sale_profile",
        "fiscal_position_id",
        help="This sale profile is applied for these fiscal positions",
    )
    code = fields.Char(
        required=True, help="Unique code of the sale profile", index=True
    )
    default = fields.Boolean(
        "Default sale profile",
        help="Define if the sale profile is used as default profile for the "
        "backend (only one default is authorized by backend)",
        index=True,
    )
    _sql_constraints = [
        (
            "constraint_unique_code",
            "unique(backend_id, code)",
            _("Code must be unique per backend."),
        )
    ]

    @api.constrains("default", "backend_id")
    def _check_default(self):
        """
        Check if there is only 1 default sale profile per backend.
        :return:
        """
        # If any of current recordset is a default sale profile, useless to
        # continue
        if not any(self.mapped("default")):
            return
        backends = self.mapped("backend_id")
        domain = [("default", "=", True), ("backend_id", "in", backends.ids)]
        group_by = "backend_id"
        groups_data = self.env["shopinvader.sale.profile"].read_group(
            domain, fields=[group_by], groupby=group_by, lazy=False
        )
        count_data = {item[group_by][0]: item.get("__count", 0) for item in groups_data}
        for record in self:
            if record.default:
                nb_default = count_data.get(record.backend_id.id, 0)
                if nb_default > 1:
                    message = _("Only one default profile is authorized")
                    raise exceptions.ValidationError(message)

    @api.constrains("backend_id", "pricelist_id", "fiscal_position_ids")
    def _check_unique_pricelist_fposition(self):
        """
        Constraint to ensure that we have only 1 pricelist per fiscal position
        on a backend.
        :return:
        """
        backends = self.mapped("backend_id")
        pricelists = self.mapped("pricelist_id")
        fiscal_positions = self.mapped("fiscal_position_ids")
        all_profiles = self.search(
            [
                ("backend_id", "in", backends.ids),
                ("pricelist_id", "in", pricelists.ids),
                ("fiscal_position_ids", "in", fiscal_positions.ids),
            ]
        )
        for record in self:
            profiles = all_profiles.filtered(
                lambda r, rec=record: r.backend_id.id == rec.backend_id.id
                and r.pricelist_id.id == rec.pricelist_id.id
                and any(
                    [
                        fpos.id in rec.fiscal_position_ids.ids
                        for fpos in r.fiscal_position_ids
                    ]
                )
            )
            if len(profiles) > 1:
                message = _(
                    "Pricelist and fiscal position combination must "
                    "be unique per backend"
                )
                raise exceptions.ValidationError(message)
