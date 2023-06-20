# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.fastapi.dependencies import (
    authenticated_partner_from_basic_auth_user,
    authenticated_partner_impl,
)

from ..routers import cart_router


# Just needed to play in the UI # TODO: remove it
class FastapiEndpoint(models.Model):

    _inherit = "fastapi.endpoint"

    app: str = fields.Selection(
        selection_add=[("cart", "Cart Demo Endpoint")], ondelete={"cart": "cascade"}
    )

    @api.model
    def _get_fastapi_routers(self):
        if self.app == "cart":
            return [cart_router]
        return super().get_fastapi_routers()

    def _get_app(self):
        app = super()._get_app()
        if self.app == "cart":
            # Here we add the override to the authenticated_partner_impl method
            authenticated_partner_impl_override = (
                authenticated_partner_from_basic_auth_user
            )
            app.dependency_overrides[
                authenticated_partner_impl
            ] = authenticated_partner_impl_override

        return app
