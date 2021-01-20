# -*- coding: utf-8 -*-
###############################################################################
#
#    Akretion France
#    Copyright (C) 2018-TODAY Akretion (<https://www.akretion.com>).
#    Author: Sylvain Calador (<https://www.akretion.com>)
#    Author: Saritha Sahadevan (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
##############################################################################

import base64
import csv
import logging
import os
import sys
from zipfile import ZipFile

from odoo import _, api, exceptions, fields, models

_logger = logging.getLogger(__name__)

try:
    import magic
    import StringIO
    import urllib2
    import validators
except (ImportError, IOError) as err:
    _logger.debug(err)


HEADERS = "default_code,tag,path"
DELIMITER = ","


class ProductImageImportWizard(models.TransientModel):

    _name = "import.product_image"

    storage_backend_id = fields.Many2one(
        "storage.backend", "Storage Backend", required=True
    )
    product_model = fields.Selection(
        [
            ("product.template", "Product template"),
            ("product.product", "Product variants"),
        ],
        string="Product Model",
        required=True,
    )
    overwrite = fields.Boolean("Overwrite image with same name")
    file_csv = fields.Binary("CSV files descriptors", required=True)
    file_zip = fields.Binary("ZIP with images", required=False)

    @api.model
    def get_image_base64(self, image_path, zip_file):
        binary = None
        if validators.url(image_path):
            binary = urllib2.urlopen(image_path).read()
        elif zip_file:
            with ZipFile(zip_file, "r") as z:
                binary = z.read(image_path)
        mimetype = magic.from_buffer(binary, mime=True)
        return mimetype, binary and base64.encodestring(binary)

    @api.model
    def get_tag(self, tag_name):
        tag_obj = self.env["image.tag"]
        tag_id = False
        if tag_name:
            tags = tag_obj.search([("name", "=", tag_name)])
            if tags:
                tag_id = tags[0].id
        return tag_id

    @api.multi
    def import_images(self):

        errors = []

        file_csv = StringIO.StringIO(base64.decodestring(self.file_csv))

        reader = csv.reader(file_csv, delimiter=DELIMITER)
        headers = next(reader, None)

        if headers != HEADERS.split(DELIMITER):
            raise exceptions.UserError(
                _("Invalid CSV file headers found! Expected: %s" % HEADERS)
            )
        csv.field_size_limit(sys.maxsize)

        file_zip = None
        if self.file_zip:
            file_zip = StringIO.StringIO(base64.decodestring(self.file_zip))

        file_obj = self.env["storage.file"]
        image_obj = self.env["storage.image"]
        relation_obj = self.env["product.image.relation"]

        for row in reader:

            if not row:
                continue

            default_code, tag_name, image_path = row
            try:
                mimetype, image_base64 = self.get_image_base64(
                    image_path, file_zip
                )
            except Exception:
                errors.append(
                    '%s: impossible to retrieve file "%s"'
                    % (default_code, image_path)
                )
                continue

            product = self.env[self.product_model].search(
                [("default_code", "=", default_code)]
            )
            if not product:
                errors.append("Could not find the product '%s'" % default_code)
                continue

            image_name = os.path.join(image_path)

            vals = {
                "data": image_base64,
                "name": image_name,
                "file_type": "image",
                "mimetype": mimetype,
                "backend_id": self.storage_backend_id.id,
            }
            file_id = file_obj.create(vals)
            tag_id = self.get_tag(tag_name)
            image = image_obj.create(
                {
                    "file_id": file_id.id,
                    "name": image_name,
                    "alt_name": image_name,
                }
            )

            if self.overwrite:
                domain = [
                    ("image_id.name", "=", image.name),
                    ("tag_id", "=", tag_id),
                    ("product_tmpl_id", "=", product.id),
                ]
                relation_obj.search(domain).unlink()

            if self.product_model == "product.template" and product:
                relation_obj.create(
                    {
                        "image_id": image.id,
                        "tag_id": tag_id,
                        "product_tmpl_id": product.id,
                    }
                )
            elif self.product_model == "product.product" and product:
                relation_obj.create(
                    {
                        "image_id": image.id,
                        "tag_id": tag_id,
                        "product_tmpl_id": product.product_tmpl_id.id,
                    }
                )

        if errors:
            raise exceptions.UserError(_("\n".join(errors)))
