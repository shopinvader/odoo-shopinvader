# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ResPartnerSerializer(models.AbstractModel):
    """The indent of this model is to provide *ONLY* model's methods and
    properties used to serialize a res.partner to a json document and
    the cerberus schema of the json result
    """

    _name = "res.partner.serializer"
    _description = "Res Partner Serializer"
    _auto = False  # non concrete table!!!!

    @api.model
    def _to_json_address(self, partner):
        return partner.jsonify(self._json_address_parser)[0]

    @property
    def _json_address_parser(self):
        return [
            "id",
            "display_name",
            "name",
            "ref",
            "street",
            "street2",
            "zip",
            "city",
            "phone",
            "mobile",
            "vat",
            "type",
            ("state_id:state", ["id", "name", "code"]),
            ("country_id:country", ["id", "name", "code"]),
            "is_company",
        ]

    @property
    def _json_address_schema(self):
        return {
            "id": {"type": "integer", "required": True, "nullable": False},
            "display_name": {
                "type": "string",
                "required": True,
                "nullable": False,
            },
            "name": {"type": "string", "required": True, "nullable": False},
            "ref": {"type": "string", "required": False, "nullable": True},
            "street": {"type": "string", "required": False, "nullable": True},
            "street2": {"type": "string", "required": False, "nullable": True},
            "zip": {"type": "string", "required": False, "nullable": True},
            "city": {"type": "string", "required": False, "nullable": True},
            "phone": {"type": "string", "required": False, "nullable": True},
            "mobile": {"type": "string", "required": False, "nullable": True},
            "vat": {"type": "string", "required": False, "nullable": True},
            "type": {
                "type": "string",
                "required": True,
                "nullable": False,
                "allowed": [
                    s[0]
                    for s in self.env["res.partner"]._fields["type"].selection
                ],
            },
            "state": {
                "type": "dict",
                "schema": {
                    "id": {
                        "type": "integer",
                        "required": True,
                        "nullable": False,
                    },
                    "code": {
                        "type": "string",
                        "required": False,
                        "nullable": True,
                    },
                    "name": {
                        "type": "string",
                        "required": True,
                        "nullable": False,
                    },
                },
                "required": False,
                "nullable": True,
            },
            "country": {
                "type": "dict",
                "schema": {
                    "id": {
                        "type": "integer",
                        "required": True,
                        "nullable": False,
                    },
                    "code": {
                        "type": "string",
                        "required": True,
                        "nullable": False,
                    },
                    "name": {
                        "type": "string",
                        "required": True,
                        "nullable": False,
                    },
                },
                "required": False,
                "nullable": True,
            },
            "is_company": {
                "type": "boolean",
                "required": True,
                "nullable": False,
            },
        }
