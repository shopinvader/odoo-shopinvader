# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component
from odoo.addons.datamodel import fields
from odoo.addons.datamodel.core import Datamodel

JSONIFY_GIFT_CARD_LINE = [
    "id",
    "amount_used",
    "validation_mode",
    ("payment_id:payment", ["id", "name"]),
    ("transaction_id:transaction", ["id", "name"]),
    ("beneficiary_id:beneficiary", ["id", "name"]),
]

JSONIFY_GIFT_CARD = [
    "id",
    "name",
    "active",
    "state",
    "is_divisible",
    "initial_amount",
    "available_amount",
    ("gift_card_tmpl_id:gift_card_tmpl", ["id", "name"]),
    "start_date",
    "end_date",
    "duration",
    "beneficiary_name",
    "beneficiary_email",
    ("buyer_id:buyer", ["id", "name"]),
    "buyer_name",
    "buyer_email",
    "comment",
    (
        "gift_card_line_id:gift_card_line_id",
        JSONIFY_GIFT_CARD_LINE,
    ),
]


class NameAndId(Datamodel):
    _name = "name.and.id"
    id = fields.Integer()
    name = fields.String()


class GiftCardSearchOutput(Datamodel):
    _name = "gift.card.search.output"
    size = fields.Integer()
    data = fields.NestedModel("gift.card.output", many=True)


class GiftCardInput(Datamodel):
    _name = "gift.card.input"
    _inherit = ["name.and.id"]

    beneficiary_name = fields.String()
    beneficiary_email = fields.String()

    buyer = fields.NestedModel("name.and.id", allow_none=True)
    buyer_name = fields.String()
    buyer_email = fields.String()

    comment = fields.String()

    initial_amount = fields.Float()

    start_date = fields.Date()

    gift_card_tmpl_id = fields.Integer()


class GiftCardLineOutput(Datamodel):
    _name = "gift.card.line.output"
    _inherit = ["name.and.id"]

    id = fields.Integer()

    amount_used = fields.Float()
    validation_mode = fields.String()

    payment = fields.NestedModel("name.and.id", allow_none=True)
    transaction = fields.NestedModel("name.and.id", allow_none=True)
    beneficiary = fields.NestedModel("name.and.id", allow_none=True)


class GiftCardOutput(Datamodel):
    _name = "gift.card.output"
    _inherit = ["name.and.id"]

    id = fields.Integer()
    name = fields.String()

    active = fields.Boolean()
    state = fields.String()
    is_divisible = fields.Boolean()

    initial_amount = fields.Float()
    available_amount = fields.Float()

    gift_card_tmpl = fields.NestedModel("name.and.id", allow_none=True)

    start_date = fields.Date()
    end_date = fields.Date()
    duration = fields.Float()

    beneficiary_name = fields.String()
    beneficiary_email = fields.String()

    buyer = fields.NestedModel("name.and.id", allow_none=True)
    buyer_name = fields.String()
    buyer_email = fields.String()

    comment = fields.String()

    gift_card_line_id = fields.NestedModel("gift.card.line.output", many=True)


class ServiceGiftCardShopinvader(Component):
    # expose Gift Card payment service under /shopinvader
    _name = "service.gift.card.shopinvader"
    _inherit = ["base.shopinvader.service"]
    _usage = "gift_card"
    _expose_model = "gift.card"

    def _parser_giftcard(self):
        return JSONIFY_GIFT_CARD

    def _to_json(self, record, many=False):
        result = record.jsonify(self._parser_giftcard())
        if many:
            return result
        else:
            return result[0]

    def _return_record(self, record):
        return self.env.datamodels["gift.card.output"].load(self._to_json(record))

    @restapi.method(
        routes=[(["/<int:id>"], "GET")],
        output_param=restapi.Datamodel("gift.card.output"),
    )
    def get(self, _id):
        record = self._get(_id)
        return self._return_record(record)

    @restapi.method(
        routes=[(["/search"], "GET")],
        output_param=restapi.Datamodel("gift.card.search.output"),
    )
    def search(self):
        domain = self._get_base_search_domain()
        records = self.env[self._expose_model].search(domain)
        result = {"size": len(records), "data": self._to_json(records, many=True)}
        return self.env.datamodels["gift.card.search.output"].load(result)

    def _get_base_search_domain(self):
        res = super()._get_base_search_domain()
        return res
