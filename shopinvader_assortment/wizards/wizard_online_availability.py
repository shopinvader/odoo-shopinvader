# Copyright 2022 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, fields, models
from odoo.exceptions import UserError


class WizardOnlineAvailability(models.TransientModel):
    """
    Wizard used to exclude products from a backend
    Product Assortment -> to_exclude
    """

    _name = "wizard.online_availability"
    _description = "Wizard Online Availability"

    backend_ids = fields.Many2many(
        "shopinvader.backend",
        string="Backend(s)",
        help="The backend(s) you want to exclude product from.",
        required=False,
        ondelete="cascade",
        domain=[("product_assortment_id", "<>", False)],
    )
    all_backend = fields.Boolean(
        string="Exclude in all backends",
        help="If checked, the product(s) will be excluded from all backend",
        default=False,
    )
    action_type = fields.Selection(
        selection=[
            ("exclude", "Exclude"),
            ("include", "Include"),
        ],
        required=True,
        help="""Include does not mean add to the product assortment
                it means, remove from exclusion.
                if product was not excluded -> no changes""",
    )

    def manage_availability(self):
        if not self.all_backend and len(self.backend_ids) == 0:
            raise UserError(
                _("You need to select a backend or check the 'all backends' option")
            )
        tmpl_ids = self.env.context.get("active_ids", False)
        if self.all_backend:
            backend_ids = self.env["shopinvader.backend"].search([])
        else:
            backend_ids = self.backend_ids

        for backend in backend_ids:

            if not backend.product_assortment_id.blacklist_product_ids.ids:
                new_blacklist = tmpl_ids
            else:
                old = set(backend.product_assortment_id.blacklist_product_ids.ids)
                new = set(tmpl_ids)

                if self.action_type == "include":
                    new_blacklist = list(old - new)

                else:
                    old.update(new)
                    new_blacklist = list(old)

            backend.product_assortment_id.write(
                {
                    "blacklist_product_ids": [(6, 0, new_blacklist)],
                }
            )
