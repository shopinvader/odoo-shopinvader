# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.component.core import AbstractComponent


class MailThreadService(AbstractComponent):
    _inherit = "base.shopinvader.service"
    _name = "shopinvader.mail.thread.abstract.service"

    def send_message(self, _id, **params):
        record = self._get(_id)
        vals = self._prepare_message_params(record, params)
        record.write({"message_ids": [(0, 0, vals)]})
        return self._to_json(record)

    def _validator_send_message(self):
        return {
            "body": {"type": "string", "required": True},
        }

    def _prepare_message_params(self, record, params):
        params["model"] = self._expose_model
        params["author_id"] = self.partner_user.id
        return params

    def _json_parser(self):
        res = [("message_ids:messages", self._json_parser_message())]
        return res

    def _json_parser_message(self):
        return [
            "id",
            "body",
            "date",
            ("author_id:author", ["id", "name"]),
        ]
