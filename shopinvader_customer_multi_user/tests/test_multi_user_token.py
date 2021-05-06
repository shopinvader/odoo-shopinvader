# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import TestMultiUserCommon


class TestMultiUserToken(TestMultiUserCommon):
    """Test partner token generation and lookup."""

    def test_token_manual_override(self):
        self.assertEqual(self.company.invader_user_token, "ABCDEF")

    def _generate_random_companies(self, count=5):
        tokens = set()
        for x in range(count):
            comp = self._create_partner(
                self.env,
                name="ACME %s" % x,
                email="acme%s@test.com" % x,
                is_company=True,
                external_id="acme{}-{}".format(x, self._get_random_hash()),
            )
            if comp.invader_user_token:
                tokens.add(comp.invader_user_token)
        return tokens

    def test_token_auto_gen_disabled(self):
        self.backend.customer_multi_user = False
        tokens = self._generate_random_companies()
        self.assertEqual(len(tokens), 0)

    def test_token_auto_gen(self):
        tokens = self._generate_random_companies()
        self.assertEqual(len(tokens), 5)
