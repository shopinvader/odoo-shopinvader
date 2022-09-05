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
EXPECTED_GET_STATES_FOR_COUNTRY = {
    "Belgium": (),
    "France": (),
    "Italy": (
        "Agrigento",
        "Alessandria",
        "Ancona",
        "Aosta",
        "Ascoli Piceno",
        "L'Aquila",
        "Arezzo",
        "Asti",
        "Avellino",
        "Bari",
        "Bergamo",
        "Biella",
        "Belluno",
        "Benevento",
        "Bologna",
        "Brindisi",
        "Brescia",
        "Barletta-Andria-Trani",
        "Bolzano",
        "Cagliari",
        "Campobasso",
        "Caserta",
        "Chieti",
        "Carbonia-Iglesias",
        "Caltanissetta",
        "Cuneo",
        "Como",
        "Cremona",
        "Cosenza",
        "Catania",
        "Catanzaro",
        "Enna",
        "Forlì-Cesena",
        "Ferrara",
        "Foggia",
        "Firenze",
        "Fermo",
        "Frosinone",
        "Genova",
        "Gorizia",
        "Grosseto",
        "Imperia",
        "Isernia",
        "Crotone",
        "Lecco",
        "Lecce",
        "Livorno",
        "Lodi",
        "Latina",
        "Lucca",
        "Monza e Brianza",
        "Macerata",
        "Messina",
        "Milano",
        "Mantova",
        "Modena",
        "Massa-Carrara",
        "Matera",
        "Napoli",
        "Novara",
        "Nuoro",
        "Ogliastra",
        "Oristano",
        "Olbia-Tempio",
        "Palermo",
        "Piacenza",
        "Padova",
        "Pescara",
        "Perugia",
        "Pisa",
        "Pordenone",
        "Prato",
        "Parma",
        "Pistoia",
        "Pesaro e Urbino",
        "Pavia",
        "Potenza",
        "Ravenna",
        "Reggio Calabria",
        "Reggio Emilia",
        "Ragusa",
        "Rieti",
        "Roma",
        "Rimini",
        "Rovigo",
        "Salerno",
        "Siena",
        "Sondrio",
        "La Spezia",
        "Siracusa",
        "Sassari",
        "Sud Sardegna",
        "Savona",
        "Taranto",
        "Teramo",
        "Trento",
        "Torino",
        "Trapani",
        "Terni",
        "Trieste",
        "Treviso",
        "Udine",
        "Varese",
        "Verbano-Cusio-Ossola",
        "Vercelli",
        "Venezia",
        "Vicenza",
        "Verona",
        "Medio Campidano",
        "Viterbo",
        "Vibo Valentia",
    ),
    "Luxembourg": (),
    "Spain": (
        "Alacant (Alicante)",
        "Albacete",
        "Almería",
        "Ávila",
        "Barcelona",
        "Badajoz",
        "Bizkaia (Vizcaya)",
        "Burgos",
        "A Coruña (La Coruña)",
        "Cádiz",
        "Cáceres",
        "Ceuta",
        "Córdoba",
        "Ciudad Real",
        "Castelló (Castellón)",
        "Cuenca",
        "Las Palmas",
        "Girona (Gerona)",
        "Granada",
        "Guadalajara",
        "Huelva",
        "Huesca",
        "Jaén",
        "Lleida (Lérida)",
        "León",
        "La Rioja",
        "Lugo",
        "Madrid",
        "Málaga",
        "Melilla",
        "Murcia",
        "Navarra (Nafarroa)",
        "Asturias",
        "Ourense (Orense)",
        "Palencia",
        "Illes Balears (Islas Baleares)",
        "Pontevedra",
        "Cantabria",
        "Salamanca",
        "Sevilla",
        "Segovia",
        "Soria",
        "Gipuzkoa (Guipúzcoa)",
        "Tarragona",
        "Teruel",
        "Santa Cruz de Tenerife",
        "Toledo",
        "València (Valencia)",
        "Valladolid",
        "Araba/Álava",
        "Zaragoza",
        "Zamora",
    ),
}

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
        for country in res:
            self.assertNotIn("states", country)

    def test_country_include_states(self):
        res = self.settings_service.dispatch(
            "countries", params={"include_states": True}
        )
        for country in res:
            self._check_names_identical(
                country["states"], EXPECTED_GET_STATES_FOR_COUNTRY[country["name"]]
            )

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
