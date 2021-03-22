# Copyright 2018-2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from werkzeug.exceptions import Forbidden, NotFound

from odoo.addons.component.core import Component


class GuestService(Component):
    _name = "shopinvader.guest.service"
    _inherit = "shopinvader.customer.service"
    _usage = "guest"

    # The following method are 'public' and can be called from the controller.
    def create(self, **params):
        if not self.shopinvader_backend.is_guest_mode_allowed:
            raise Forbidden("Guest mode not allowed.")
        params["is_guest"] = True
        self._archive_existing_binding(params["email"])
        resp = super().create(**params)
        resp["store_cache"]["customer"]["is_guest"] = True
        return resp

    def search(self, email):
        """
        Search for guest with email
        :param email:
        """
        res = self._get_binding(email)
        return {"found": len(res) > 0}

    def register(self, email, external_id):
        """
        Called to transform a guest account into a registered curtomer account
        :param email:
        :param external_id:
        """
        binding = self._get_binding(email)
        if not binding:
            raise NotFound(email)
        binding.write({"is_guest": False, "external_id": external_id})
        self.work.partner = binding.record_id
        return self._prepare_create_response(binding)

    def stop(self, email):
        """
        Called to invalidate the guest mode into the current session
        """
        binding = self._get_binding(email)
        if not binding:
            raise NotFound(email)
        return {"store_cache": {"customer": {}}}

    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

    def _validator_create(self):
        schema = super()._validator_create()
        if "external_id" in schema:
            schema.pop("external_id")
        return schema

    def _validator_search(self):
        return {"email": {"type": "string", "required": True}}

    def _validator_return_search(self):
        return {"found": {"type": "boolean", "required": True}}

    def _validator_register(self):
        return {
            "email": {"type": "string", "required": True},
            "external_id": {"type": "string", "required": True},
        }

    def _validator_stop(self):
        return {"email": {"type": "string", "required": True}}

    def _send_welcome_message(self, binding):
        if binding.is_guest:
            self.shopinvader_backend._send_notification(
                "guest_customer_welcome", binding.record_id
            )
        else:
            super()._send_welcome_message(binding)

    def _get_binding(self, email):
        domain = [
            ("email", "=", email),
            ("is_guest", "=", True),
            ("backend_id", "=", self.shopinvader_backend.id),
        ]
        return self.env["shopinvader.partner"].search(domain, limit=1)

    def _archive_existing_binding(self, email):
        """
        If a previous guest binding already exists: Archive...
        """
        binding = self._get_binding(email)
        if binding:
            binding.active = False
            binding.flush()

    def _to_customer_info(self, partner):
        info = super()._to_customer_info(partner)
        info.update({"email": self.partner.email})
        return info
