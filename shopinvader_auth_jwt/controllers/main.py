# Copyright 20201 ACSONE SA/NV (http://acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _
from odoo.exceptions import MissingError
from odoo.http import request, route

from odoo.addons.base_rest.controllers import main

_logger = logging.getLogger(__name__)


class InvaderController(main.RestController):

    _root_path = "/shopinvader_jwt/"
    _collection_name = "shopinvader.backend"
    _default_auth = "jwt_shopinvader"

    @route(
        ["/shopinvader/<service>/<int:_id>/download"],
        methods=["GET", "OPTIONS"],
        auth=_default_auth,
    )
    def service_download(self, service, _id=None, **params):
        params["id"] = _id
        return self._process_method(service, "download", _id, params=params)

    @classmethod
    def _get_shopinvader_partner_from_jwt(cls):
        partner_model = request.env["shopinvader.partner"]
        partner_email = request.jwt_payload.get("email")
        backend = cls._get_shopinvader_backend_from_request()
        if partner_email:
            shopinvader_partner = cls._find_partner(backend, partner_email)
            if len(shopinvader_partner) == 1:
                cls._validate_partner(backend, shopinvader_partner)
                return shopinvader_partner
            else:
                _logger.warning("Wrong HTTP_PARTNER_EMAIL, header ignored")
                if len(shopinvader_partner) > 1:
                    _logger.warning(
                        "More than one shopinvader.partner found for:"
                        " backend_id={} email={}".format(backend.id, partner_email)
                    )
                # Could be because the email is not related to a partner or
                # because the partner is inactive
                raise MissingError(_("The given partner is not found!"))
        return partner_model.browse([])

    @classmethod
    def _find_partner(cls, backend, partner_email):
        partner_domain = [
            ("partner_email", "=", partner_email),
            ("backend_id", "=", backend.id),
        ]
        return request.env["shopinvader.partner"].search(partner_domain, limit=2)

    @classmethod
    def _validate_partner(cls, backend, partner):
        with backend.work_on("res.partner") as work:
            validator = work.component(usage="partner.validator")
            validator.validate_partner(partner)

    @classmethod
    def _get_shopinvader_backend_from_request(cls):
        backend_model = request.env["shopinvader.backend"]
        return backend_model._get_from_jwt_aud(request.jwt_payload.get("aud"))

    def _get_component_context(self):
        """Retrieve service component work context.

        Main keys to look for:

        * partner_user: the partner of the current user (matching via email)
        * partner: every service will use it as the current partner (eg: customer info)
        * cart_id: sale order ID used to keep in sync client and backend
        * shopinvader_backend: current shopinvader backend (matching API key)
        """
        res = super(InvaderController, self)._get_component_context()
        res["shopinvader_backend"] = self._get_shopinvader_backend_from_request()
        # TODO: all services should rely on shopinvader partner
        # rather than the real partner. SBI: why?
        shopinvader_partner = self._get_shopinvader_partner_from_jwt()
        res["invader_partner"] = shopinvader_partner
        partner = shopinvader_partner.record_id
        res["partner_user"] = partner
        # The partner user for the main account or for sale order may differ.
        res["partner"] = partner.get_shop_partner(res["shopinvader_backend"])
        return res
