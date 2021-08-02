# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


import base64
import datetime

from babel.dates import format_datetime

from odoo import _
from odoo.http import request

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class TicketService(Component):
    """Shopinvader service to manage helpdesk tickets."""

    _name = "shopinvader.helpdesk.ticket.service"
    _inherit = "shopinvader.mail.thread.abstract.service"
    _usage = "helpdesk.ticket"
    _expose_model = "helpdesk.ticket"
    _description = __doc__

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it !

    def get(self, _id):
        record = self._get(_id)
        return self._to_json(record)

    def search(self, **params):
        return self._paginate_search(**params)

    # pylint: disable=W8106
    def create(self, **params):
        vals = self._prepare_params(params.copy())
        record = self.env[self._expose_model].create(vals)
        return {"data": self._to_json(record)}

    def update(self, _id, **params):
        # TODO: delete and only allow to add attachments
        record = self._get(_id)
        record.write(self._prepare_params(params.copy(), mode="update"))
        return self.search()

    def cancel(self, _id):
        self._get(_id).unlink()
        return self.search()

    @restapi.method(
        routes=[(["/<int:_id>/upload"], "POST")],
        input_param=restapi.BinaryData(
            mediatypes=["application/pdf", "image/jpeg", "image/png"], required=True
        ),
    )
    def upload(self, _id, **params):
        record = self._get(_id)
        req = request.httprequest
        self.env["ir.attachment"].create(
            {
                "res_id": record.id,
                "res_model": record._name,
                "name": "Client upload: {}".format(
                    format_datetime(datetime.datetime.now())
                ),
                "datas": base64.encodebytes(req.get_data()),
            }
        )
        return self._to_json(record)

    def _validator_get(self):
        return {}

    def _validator_search(self):
        return {
            "id": {"coerce": to_int, "type": "integer"},
            "per_page": {
                "coerce": to_int,
                "nullable": True,
                "type": "integer",
            },
            "page": {"coerce": to_int, "nullable": True, "type": "integer"},
            "scope": {"type": "dict", "nullable": True},
        }

    def _validator_create(self):
        return {
            "name": {"type": "string", "required": True, "empty": False},
            "description": {"type": "string", "required": True, "empty": False},
            "partner_email": {
                "type": "string",
                "nullable": True,
            },
            "partner_name": {
                "type": "string",
                "nullable": True,
            },
            "category_id": {
                "type": "integer",
                "coerce": to_int,
                "nullable": True,
            },
        }

    def _prepare_params(self, params, mode="create"):
        if mode == "create":
            params["shopinvader_backend_id"] = self.shopinvader_backend.id
            params["channel_id"] = self.shopinvader_backend.helpdesk_channel_id.id
            if self.partner_user:
                params["partner_id"] = self.partner_user.id
            elif params.get("partner_email"):
                params["partner_id"] = (
                    self.env["res.partner"]
                    .find_or_create(params["partner_email"], assert_valid_email=True)
                    .id
                )
            else:
                raise AttributeError(_("The email is mandatory"))
        return params

    def _json_parser(self):
        res = super()._json_parser()
        res.extend(
            [
                "id",
                "name",
                "description",
                "create_date",
                "last_stage_update",
                ("category_id:category", ["id", "name"]),
                ("stage_id:stage", ["id", "name"]),
                ("attachment_ids:attachments", ["id", "name"]),
            ]
        )
        return res

    def _to_json(self, ticket, **kw):
        data = ticket.jsonify(self._json_parser())
        return data
