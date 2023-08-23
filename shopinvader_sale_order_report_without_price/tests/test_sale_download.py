import mock

from odoo.addons.shopinvader_restapi.services import abstract_download
from odoo.addons.shopinvader_restapi.tests.test_sale import CommonSaleCase


class SaleCase(CommonSaleCase):
    def download(self, id, **params):
        with mock.patch(
            "odoo.addons.shopinvader_restapi.services."
            "abstract_download.content_disposition"
        ) as mocked_cd:
            request = mock.MagicMock()
            abstract_download.request = request
            mocked_cd.return_value = "attachment; filename=test"
            self.service.download(id, **params)
            self.assertEqual(1, request.make_response.call_count)
            content, headers = request.make_response.call_args[0]
            self.assertTrue(content)
            self.assertIn(("Content-Disposition", "attachment; filename=test"), headers)
            return content.decode("utf-8")

    def test_sale_order_report_without_price(self):
        self.sale.action_confirm_cart()
        report_with_price = self.download(self.sale.id, no_price=False)
        prices = [
            "885.00",
            "2,655.00",
            "2,950.00",
            "5,900.00",
            "8,555.00",
        ]
        for price in prices:
            self.assertIn(price, report_with_price)

        report_without_price = self.download(self.sale.id, no_price=True)
        for price in prices:
            self.assertNotIn(price, report_without_price)

    def test_sale_order_report_without_price_default_with_price(self):
        self.sale.action_confirm_cart()
        default_report = self.download(self.sale.id)
        report_with_price = self.download(self.sale.id, no_price=False)
        self.assertEquals(default_report, report_with_price)
