import contextlib
import time
from unittest.mock import Mock

import jwt

import odoo.http
from odoo.tools.misc import DotDict

from odoo.addons.shopinvader.tests.test_cart import CommonConnectedCartCase


class TestTransferCart(CommonConnectedCartCase):
    @contextlib.contextmanager
    def _mock_request(self, authorization):
        environ = {}
        if authorization:
            environ["HTTP_AUTHORIZATION"] = authorization
        request = Mock(
            context={},
            db=self.env.cr.dbname,
            uid=None,
            httprequest=Mock(environ=environ, headers={}),
            session=DotDict(),
            env=self.env,
            cr=self.env.cr,
        )
        # These attributes are added upon successful auth, so make sure
        # calling hasattr on the mock when they are not yet set returns False.
        del request.jwt_payload
        del request.jwt_partner_id

        with contextlib.ExitStack() as s:
            odoo.http._request_stack.push(request)
            s.callback(odoo.http._request_stack.pop)
            yield request

    def _create_token(
        self,
        key="thesecret",
        audience="me",
        issuer="http://the.issuer",
        exp_delta=100,
        nbf=None,
        email=None,
    ):
        payload = dict(aud=audience, iss=issuer, exp=time.time() + exp_delta)
        if email:
            payload["email"] = email
        if nbf:
            payload["nbf"] = nbf
        return jwt.encode(payload, key=key, algorithm="HS256")

    def _create_validator(
        self,
        name,
        audience="me",
        issuer="http://the.issuer",
        secret_key="thesecret",
        partner_id_required=False,
        partner_id_strategy="email",
    ):
        return self.env["auth.jwt.validator"].create(
            dict(
                name=name,
                signature_type="secret",
                secret_algorithm="HS256",
                secret_key=secret_key,
                audience=audience,
                issuer=issuer,
                user_id_strategy="static",
                partner_id_strategy=partner_id_strategy,
                partner_id_required=partner_id_required,
            )
        )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_1 = cls.env.ref("product.product_product_4b")
        cls.product_2 = cls.env.ref("product.product_product_13")
        cls.product_3 = cls.env.ref("product.product_product_11")

    def setUp(self):
        super().setUp()

        with self.work_on_services(partner=self.partner) as work:
            self.service = work.component(usage="cart")

        self.guest = self.env.ref("shopinvader.partner_2")
        with self.work_on_services(partner=self.guest) as work:
            self.guest_service = work.component(usage="cart")

        self.guest_cart = self.env.ref("shopinvader.sale_order_3")
        self.token = self._create_token(email=self.partner.email)
        self.guest_token = self._create_token(email=self.guest.email)
        self._create_validator("shopinvader")

    def test_cart_transfer(self):
        self.cart.unlink()
        self.service.dispatch("search")
        self.service.dispatch(
            "add_item", params={"product_id": self.product_1.id, "item_qty": 2}
        )
        self.service.dispatch(
            "add_item", params={"product_id": self.product_2.id, "item_qty": 1}
        )

        self.guest_cart.unlink()
        self.guest_service.dispatch("search")
        self.guest_service.dispatch(
            "add_item", params={"product_id": self.product_3.id, "item_qty": 2}
        )
        self.guest_service.dispatch(
            "add_item", params={"product_id": self.product_2.id, "item_qty": 5}
        )

        # Logged in cart
        cart = self.service.dispatch("search")["data"]
        self.assertEquals(cart["lines"]["count"], 3)

        self.assertEquals(
            cart["lines"]["items"][0]["name"],
            "[FURN_0097] Customizable Desk (CONFIG) (Steel, Black)\n160x80cm, with large legs.",
        )
        self.assertEquals(cart["lines"]["items"][0]["qty"], 2)
        self.assertEquals(
            cart["lines"]["items"][1]["name"], "[FURN_1118] Corner Desk Left Sit"
        )
        self.assertEquals(cart["lines"]["items"][1]["qty"], 1)

        # Guest cart
        guest_cart = self.guest_service.dispatch("search")["data"]
        self.assertEquals(guest_cart["lines"]["count"], 7)
        self.assertEquals(
            guest_cart["lines"]["items"][0]["name"],
            "[E-COM12] Conference Chair (CONFIG) (Steel)",
        )
        self.assertEquals(guest_cart["lines"]["items"][0]["qty"], 2)
        self.assertEquals(
            guest_cart["lines"]["items"][1]["name"], "[FURN_1118] Corner Desk Left Sit"
        )
        self.assertEquals(guest_cart["lines"]["items"][1]["qty"], 5)

        # Transfer guest to logged in cart

        with self._mock_request("Bearer " + self.guest_token):
            transferred_cart = self.guest_service.dispatch(
                "transfer", params={"token": self.token}
            )["data"]

        self.assertEquals(transferred_cart["lines"]["count"], 7)
        self.assertEquals(
            transferred_cart["lines"]["items"][0]["name"],
            "[E-COM12] Conference Chair (CONFIG) (Steel)",
        )
        self.assertEquals(transferred_cart["lines"]["items"][0]["qty"], 2)
        self.assertEquals(
            transferred_cart["lines"]["items"][1]["name"],
            "[FURN_1118] Corner Desk Left Sit",
        )
        self.assertEquals(transferred_cart["lines"]["items"][1]["qty"], 5)

        self.assertEquals(self.service.dispatch("search")["data"], transferred_cart)

    def test_cart_transfer_merge(self):
        self.backend.merge_cart_on_transfer = True

        self.cart.unlink()
        self.service.dispatch("search")
        self.service.dispatch(
            "add_item", params={"product_id": self.product_1.id, "item_qty": 2}
        )
        self.service.dispatch(
            "add_item", params={"product_id": self.product_2.id, "item_qty": 1}
        )

        self.guest_cart.unlink()
        self.guest_service.dispatch("search")
        self.guest_service.dispatch(
            "add_item", params={"product_id": self.product_3.id, "item_qty": 2}
        )
        self.guest_service.dispatch(
            "add_item", params={"product_id": self.product_2.id, "item_qty": 5}
        )

        # Logged in cart
        cart = self.service.dispatch("search")["data"]
        self.assertEquals(cart["lines"]["count"], 3)

        self.assertEquals(
            cart["lines"]["items"][0]["name"],
            "[FURN_0097] Customizable Desk (CONFIG) (Steel, Black)\n160x80cm, with large legs.",
        )
        self.assertEquals(cart["lines"]["items"][0]["qty"], 2)
        self.assertEquals(
            cart["lines"]["items"][1]["name"], "[FURN_1118] Corner Desk Left Sit"
        )
        self.assertEquals(cart["lines"]["items"][1]["qty"], 1)

        # Guest cart
        guest_cart = self.guest_service.dispatch("search")["data"]
        self.assertEquals(guest_cart["lines"]["count"], 7)
        self.assertEquals(
            guest_cart["lines"]["items"][0]["name"],
            "[E-COM12] Conference Chair (CONFIG) (Steel)",
        )
        self.assertEquals(guest_cart["lines"]["items"][0]["qty"], 2)
        self.assertEquals(
            guest_cart["lines"]["items"][1]["name"], "[FURN_1118] Corner Desk Left Sit"
        )
        self.assertEquals(guest_cart["lines"]["items"][1]["qty"], 5)

        # Transfer guest to logged in cart

        with self._mock_request("Bearer " + self.guest_token):
            transferred_cart = self.guest_service.dispatch(
                "transfer", params={"token": self.token}
            )["data"]

        self.assertEquals(transferred_cart["lines"]["count"], 10)
        self.assertEquals(
            transferred_cart["lines"]["items"][0]["name"],
            "[E-COM12] Conference Chair (CONFIG) (Steel)",
        )
        self.assertEquals(transferred_cart["lines"]["items"][0]["qty"], 2)
        self.assertEquals(
            transferred_cart["lines"]["items"][1]["name"],
            "[FURN_1118] Corner Desk Left Sit",
        )
        self.assertEquals(transferred_cart["lines"]["items"][1]["qty"], 6)
        self.assertEquals(
            transferred_cart["lines"]["items"][2]["name"],
            "[FURN_0097] Customizable Desk (CONFIG) (Steel, Black)\n160x80cm, with large legs.",
        )
        self.assertEquals(transferred_cart["lines"]["items"][2]["qty"], 2)

        self.assertEquals(self.service.dispatch("search")["data"], transferred_cart)

    def test_cart_transfer_merge_no_cart(self):
        self.backend.merge_cart_on_transfer = True

        self.cart.unlink()

        self.guest_cart.unlink()
        self.guest_service.dispatch("search")
        self.guest_service.dispatch(
            "add_item", params={"product_id": self.product_3.id, "item_qty": 2}
        )
        self.guest_service.dispatch(
            "add_item", params={"product_id": self.product_2.id, "item_qty": 5}
        )

        # Guest cart
        guest_cart = self.guest_service.dispatch("search")["data"]
        self.assertEquals(guest_cart["lines"]["count"], 7)
        self.assertEquals(
            guest_cart["lines"]["items"][0]["name"],
            "[E-COM12] Conference Chair (CONFIG) (Steel)",
        )
        self.assertEquals(guest_cart["lines"]["items"][0]["qty"], 2)
        self.assertEquals(
            guest_cart["lines"]["items"][1]["name"], "[FURN_1118] Corner Desk Left Sit"
        )
        self.assertEquals(guest_cart["lines"]["items"][1]["qty"], 5)

        # Transfer guest to logged in cart

        with self._mock_request("Bearer " + self.guest_token):
            transferred_cart = self.guest_service.dispatch(
                "transfer", params={"token": self.token}
            )["data"]

        self.assertEquals(transferred_cart["lines"]["count"], 7)
        self.assertEquals(
            transferred_cart["lines"]["items"][0]["name"],
            "[E-COM12] Conference Chair (CONFIG) (Steel)",
        )
        self.assertEquals(transferred_cart["lines"]["items"][0]["qty"], 2)
        self.assertEquals(
            transferred_cart["lines"]["items"][1]["name"],
            "[FURN_1118] Corner Desk Left Sit",
        )
        self.assertEquals(transferred_cart["lines"]["items"][1]["qty"], 5)

        self.assertEquals(self.service.dispatch("search")["data"], transferred_cart)
