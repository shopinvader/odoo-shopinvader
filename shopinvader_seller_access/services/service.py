from odoo import _
from odoo.exceptions import AccessDenied
from odoo.http import request

from odoo.addons.component.core import AbstractComponent


class BaseShopinvaderService(AbstractComponent):
    _inherit = "base.shopinvader.service"

    def check_seller_access(self):
        """
        Check if the current backend is configured to support seller access
        and current logged user is a seller
        """

        backend = self.shopinvader_backend

        if not backend.seller_access:
            raise AccessDenied(_("This backend does not support seller access"))

        if not hasattr(request, "jwt_payload"):
            raise AccessDenied(_("Seller access only work with JWT auth"))

        groups = request.jwt_payload.get("groups")
        if not groups:
            raise AccessDenied(_("JWT has no groups claim"))

        if not backend.seller_access_group_name:
            raise AccessDenied(
                _("Seller access group name is not configured on backend")
            )

        if backend.seller_access_group_name not in groups:
            raise AccessDenied(
                _("{} group is required and not present in {}").format(
                    backend.seller_access_group_name, groups
                )
            )

    @property
    def has_seller_access(self):
        try:
            self.check_seller_access()
            return True
        except (AccessDenied, RuntimeError):
            # Also catch RuntimeError which is raise in tests when request is
            # not bound
            return False
