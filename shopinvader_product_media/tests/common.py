# Copyright 2024 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import base64

from odoo.tools import file_open


class Mixin:
    @staticmethod
    def _get_file_content(
        filename, base_path=None, as_binary=False, module="shopinvader_product_media"
    ):
        with file_open("%s/tests/fixture/%s" % (module, filename), "rb") as f:
            data = f.read()
            if as_binary:
                return data
            return base64.b64encode(data)

    @classmethod
    def _create_storage_media(cls, name):
        return cls.env["storage.media"].create(
            {"name": name, "data": cls._get_file_content(name)}
        )
