# Copyright 2022 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    @restapi.method(
        routes=[(["/attachments"], "POST")],
        input_param=restapi.MultipartFormData(
            {
                "file": restapi.BinaryData(required=True),
                "params": restapi.Datamodel("ir.attachment.input"),
            }
        ),
        output_param=restapi.Datamodel("ir.attachment.output"),
    )
    def create_attachment(self, file=None, params=None):
        cart = self._get()
        return super().create_attachment(object_id=cart.id, file=file, params=params)

    @restapi.method(
        routes=[(["/attachments/<int:attachment_id>"], "GET")],
        output_param=restapi.BinaryData(required=True),
    )
    def download_attachment(self, attachment_id=None):
        cart = self._get()
        return super().download_attachment(
            object_id=cart.id, attachment_id=attachment_id
        )
