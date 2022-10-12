from odoo.addons.shopinvader.tests.common import CommonCase

from .common import SellerGroupBackendMixin


class TestQuotation(SellerGroupBackendMixin, CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if "shopinvader_quotation" not in cls.env.registry._init_modules:
            cls.__unittest_skip__ = True
            cls.__unittest_skip_why__ = "shopinvader_quotation not installed"
            return

        cls.partner = cls.env.ref("shopinvader.partner_1")
        cls.partner_2 = cls.env.ref("shopinvader.partner_2")
        cls.user_of_partner_2 = cls.env["res.users"].create(
            {
                "login": "partner_2",
                "partner_id": cls.partner_2.id,
            }
        )

        cls.so1 = cls.env["sale.order"].create(
            {
                "typology": "quotation",
                "partner_id": cls.partner.id,
                "shopinvader_backend_id": cls.backend.id,
            }
        )
        cls.so2 = cls.env["sale.order"].create(
            {
                "typology": "quotation",
                "partner_id": cls.partner.id,
                "user_id": cls.user_of_partner_2.id,
                "shopinvader_backend_id": cls.backend.id,
            }
        )
        cls.so3 = cls.env["sale.order"].create(
            {
                "typology": "quotation",
                "partner_id": cls.partner_2.id,
                "shopinvader_backend_id": cls.backend.id,
            }
        )

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        with self.work_on_services(
            partner=self.partner, shopinvader_session=self.shopinvader_session
        ) as work:
            self.quotation_service = work.component(usage="quotations")
        # We have no session here
        with self.work_on_services(partner=self.partner_2) as work:
            self.service_as_seller = work.component(usage="quotations")

    def test_search_quotation_as_customer(self):
        sales = self.quotation_service.dispatch(
            "search",
        )["data"]
        self.assertEquals(len(sales), 2)
        self.assertEquals(sales[0]["id"], self.so2.id)
        self.assertEquals(sales[1]["id"], self.so1.id)

    def test_search_quotation_as_customer_2(self):
        sales = self.service_as_seller.dispatch(
            "search",
        )["data"]
        self.assertEquals(len(sales), 1)
        self.assertEquals(sales[0]["id"], self.so3.id)

    def test_search_quotation_as_seller(self):
        with self.seller_group():
            sales = self.service_as_seller.dispatch(
                "search",
            )["data"]
        self.assertEquals(len(sales), 2)
        self.assertEquals(sales[0]["id"], self.so3.id)
        self.assertEquals(sales[1]["id"], self.so2.id)

    def test_search_quotation_as_seller_bad_group(self):
        with self.seller_group("buyer"):
            sales = self.service_as_seller.dispatch(
                "search",
            )["data"]
        self.assertEquals(len(sales), 1)
        self.assertEquals(sales[0]["id"], self.so3.id)
