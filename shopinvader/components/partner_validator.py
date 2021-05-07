# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component

# TODO: this exception is not handled yet on Locomotive side.
# Currently if we raise the error the frontend is broken.
# Hence, let's rely on `enabled` flag to adjust the UI
# until we handle the exception client side,
# from ..exceptions import PartnerNotValidatedError


class PartnerValidator(Component):
    _name = "shopinvader.partner.validator"
    _inherit = "base.shopinvader.component"
    _usage = "partner.validator"
    _apply_on = "res.partner"

    def validate_partner(self, partner):
        if self.backend.validate_customers:
            validator = getattr(
                self,
                "_validate_partner_{}".format(
                    self.backend.validate_customers_type
                ),
                lambda partner: True,
            )
            # TODO: this should raise an exception if not satisfied
            # but the validation is done in the controller
            # and the frontend is not able to handle it properly yet.
            # See `InvaderController._get_partner_from_headers`
            validator(partner)

    def _validate_partner_all(self, partner):
        if not partner.is_shopinvader_active:
            # raise PartnerNotValidatedError(
            #     "Customer found but not validated yet."
            # )
            pass

    def _validate_partner_address(self, partner):
        if (
            not partner.is_shopinvader_active
            and not partner.address_type == "address"
        ):
            # raise PartnerNotValidatedError(
            #     "Address found but not validated yet."
            # )
            pass

    def _validate_partner_company(self, partner):
        if (
            not partner.is_shopinvader_active
            and partner.is_company
            and partner.address_type == "profile"
        ):
            # raise PartnerNotValidatedError(
            #     "Company found but not validated yet."
            # )
            pass

    def _validate_partner_user(self, partner):
        if (
            not partner.is_shopinvader_active
            and not partner.is_company
            and partner.address_type == "profile"
        ):
            # raise PartnerNotValidatedError(
            #     "Customer found but not validated yet."
            # )
            pass

    def _validate_partner_company_and_user(self, partner):
        self._validate_partner_company(partner)
        self._validate_partner_user(partner)

    def _allowed_partner_types(self):
        return [x[0] for x in self.model._fields["address_type"].selection]

    def enabled_by_params(self, params, partner_type="profile"):
        """Check if partner is enabled via given params by given partner type.

        This is mostly used by services to check if the partner
        they are dealing with is enabled or should be enabled (create case).
        """
        assert partner_type in self._allowed_partner_types()
        if not self.backend.validate_customers:
            return True
        backend_policy = self.backend.validate_customers_type
        if backend_policy == "all":
            return False
        handler = getattr(
            self,
            "_enabled_by_params_for_{}".format(partner_type),
            lambda backend_policy, params: True,
        )
        return handler(backend_policy, params)

    def _enabled_by_params_for_profile(self, backend_policy, params):
        """Check if enabled by partner type == "profile"."""
        is_company = "is_company" in params and params["is_company"]
        if backend_policy == "company":
            return not is_company
        elif backend_policy == "user":
            if "is_company" not in params:
                # definetely not a company
                return False
            # rely on the flag: got a company -> enabled
            return is_company
        elif backend_policy == "company_and_user":
            return False
        return True

    def _enabled_by_params_for_address(self, backend_policy, params):
        """Check if enabled by partner type == "address"."""
        if backend_policy == "address":
            return not params["is_company"] and params.get("parent_id")
        return True

    def is_partner_validated(self, partner):
        """Check if given partner is enabled for current backend."""
        if (
            self.backend.validate_customers
            and not partner.is_shopinvader_active
        ):
            return False
        return True
