# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from .common import CommonCase


class TestPartnerValidation(CommonCase):
    def test_validation_profile_customer(self):
        with self.backend.work_on("res.partner") as work:
            validator = work.component(usage="partner.validator")
        # no validation required: always enabled
        self.assertFalse(self.backend.validate_customers)
        self.assertTrue(validator.enabled_by_params({}))
        # no validation required for all: disabled
        self.backend.update(
            dict(validate_customers=True, validate_customers_type="all")
        )
        self.assertFalse(validator.enabled_by_params({}))

        # validation required for companies
        self.backend.validate_customers_type = "company"
        # no company: enabled
        self.assertTrue(validator.enabled_by_params({}))
        # yes company: disabled
        self.assertFalse(validator.enabled_by_params({"is_company": True}))

        # validation required for companies and users
        self.backend.validate_customers_type = "company_and_user"
        # company or not: disabled
        self.assertFalse(validator.enabled_by_params({}))
        self.assertFalse(validator.enabled_by_params({"is_company": True}))

        # validation required for users only
        self.backend.validate_customers_type = "user"
        # no company: disabled
        self.assertFalse(validator.enabled_by_params({}))
        # yes company: enabled
        self.assertTrue(validator.enabled_by_params({"is_company": True}))

    def test_validation_profile_address(self):
        with self.backend.work_on("res.partner") as work:
            validator = work.component(usage="partner.validator")
        # no validation required: always enabled
        self.assertFalse(self.backend.validate_customers)
        self.assertTrue(
            validator.enabled_by_params({}, partner_type="address")
        )
        # no validation required for all: disabled
        self.backend.update(
            dict(validate_customers=True, validate_customers_type="all")
        )
        self.assertFalse(
            validator.enabled_by_params({}, partner_type="address")
        )

        # validation required for companies
        self.backend.validate_customers_type = "company"
        # no company: enabled
        self.assertTrue(
            validator.enabled_by_params({}, partner_type="address")
        )
        # yes company: enabled as address validation ignores company state
        self.assertTrue(
            validator.enabled_by_params(
                {"is_company": True}, partner_type="address"
            )
        )

        # validation required for companies and users
        self.backend.validate_customers_type = "company_and_user"
        # company or not: address are allowed
        self.assertTrue(
            validator.enabled_by_params({}, partner_type="address")
        )
        self.assertTrue(
            validator.enabled_by_params(
                {"is_company": True}, partner_type="address"
            )
        )
        # same for user
        self.backend.validate_customers_type = "user"
        # no company: enabled
        self.assertTrue(
            validator.enabled_by_params({}, partner_type="address")
        )
        # yes company: enabled
        self.assertTrue(
            validator.enabled_by_params(
                {"is_company": True}, partner_type="address"
            )
        )
