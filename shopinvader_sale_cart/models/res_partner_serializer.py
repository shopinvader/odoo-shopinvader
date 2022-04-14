# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ResPartnerSerializer(models.AbstractModel):
    _inherit = "res.partner.serializer"

    @property
    def _json_address_parser(self):
        parser = super(ResPartnerSerializer, self)._json_address_parser
        parser.append("address_type")
        return parser

    @property
    def _json_address_schema(self):
        schema = super(ResPartnerSerializer, self)._json_address_schema
        schema["address_type"] = {
            "type": "string",
            "required": True,
            "nullable": False,
            "allowed": [
                s
                for s in self.env["res.partner"]
                ._fields["address_type"]
                .get_values(self.env)
            ],
        }
        return schema
