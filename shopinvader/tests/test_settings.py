# Copyright 2021 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import CommonCase

EXPECTED_GET_COUNTRY = (
    "Belgium",
    "France",
    "Italy",
    "Luxembourg",
    "Spain",
)
EXPECTED_GET_TITLE = (
    "Doctor",
    "Madam",
    "Miss",
    "Mister",
    "Professor",
)
EXPECTED_GET_INDUSTRY = (
    "Administrative",
    "Agriculture",
    "Construction",
    "Education",
    "Energy supply",
    "Entertainment",
    "Extraterritorial",
    "Finance/Insurance",
    "Food",
    "Health/Social",
    "Households",
    "IT/Communication",
    "Manufacturing",
    "Mining",
    "Other Services",
    "Public Administration",
    "Real Estate",
    "Scientific",
    "Transportation",
    "Water supply",
    "Wholesale/Retail",
)
EXPECTED_GET_CURRENCY = ["EUR", "USD"]
EXPECTED_GET_LANG = ["English (US)"]


class SettingsTestCase(CommonCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        with self.work_on_services(
            partner=self.env.ref("shopinvader.partner_1")
        ) as work:
            self.settings_service = work.component(usage="settings")

    def _check_names_identical(self, to_check, expected_vals):
        actual_vals = {el["name"] for el in to_check}
        self.assertSetEqual(set(expected_vals), actual_vals)

    def test_country(self):
        res = self.settings_service.dispatch("countries")
        self._check_names_identical(res, EXPECTED_GET_COUNTRY)

    def test_title(self):
        res = self.settings_service.dispatch("titles")
        self._check_names_identical(res, EXPECTED_GET_TITLE)

    def test_industry(self):
        res = self.settings_service.dispatch("industries")
        self._check_names_identical(res, EXPECTED_GET_INDUSTRY)

    def test_currency(self):
        res = self.settings_service.dispatch("currencies")
        self._check_names_identical(res, EXPECTED_GET_CURRENCY)

    def test_lang(self):
        res = self.settings_service.dispatch("languages")
        self._check_names_identical(res, EXPECTED_GET_LANG)

    def test_all(self):
        res = self.settings_service.dispatch("get_all")
        self._check_names_identical(res["countries"], EXPECTED_GET_COUNTRY)
        self._check_names_identical(res["titles"], EXPECTED_GET_TITLE)
        self._check_names_identical(res["industries"], EXPECTED_GET_INDUSTRY)
        self._check_names_identical(res["currencies"], EXPECTED_GET_CURRENCY)
        self._check_names_identical(res["languages"], EXPECTED_GET_LANG)
