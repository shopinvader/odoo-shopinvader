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

import csv
import urllib2
import base64
import StringIO
import sys
from zipfile import ZipFile

import validators
from odoo import models, fields, api
from odoo.exceptions import Warning


HEADERS = 'default_code,tag,path'
DELIMITER = ','


class ProductImageImportWizard(models.TransientModel):

    _name = 'import.product_image'

    product_model = fields.Selection([
        ('product.template', 'Product template'),
        ('product.product', 'Product variants')
    ], string="Product Model")
    overwrite = fields.Boolean('Overwrite image with same name')
    file_csv = fields.Binary('CSV files descriptors', required=True)
    file_zip = fields.Binary('ZIP with images', required=False)

    @api.multi
    def import_images(self):

        errors = []

        file_csv = StringIO.StringIO(base64.decodestring(self.file_csv))

        reader = csv.reader(file_csv, delimiter=DELIMITER)
        headers = next(reader, None)

        if headers != HEADERS.split(DELIMITER):
            raise Warning(
                'Invalid CSV file headers found! Expected: %s' % HEADERS
            )
        csv.field_size_limit(sys.maxsize)

        file_zip = StringIO.StringIO(base64.decodestring(self.file_zip))

        file_obj = self.env['storage.file']
        image_obj = self.env['storage.image']
        tag_obj = self.env['image.tag']
        relation_obj = self.env['product.image.relation']

        def get_image_base64(image_path, zip_file):
            binary = None
            if validators.url(image_path):
                binary = urllib2.urlopen(image_path).read()
            elif zip_file:
                with ZipFile(zip_file, 'r') as z:
                    binary = z.read(image_path)
            return binary and base64.encodestring(binary)

        def get_tag(tag_name):
            tag_id = False
            if tag_name:
                tags = tag_obj.search([('name', '=', tag_name)])
                if tags:
                    tag_id = tags[0].id
            return tag_id

        for row in reader:

            if not row:
                continue

            default_code, tag_name, image_path = row
            try:
                image_base64 = get_image_base64(image_path, file_zip)
            except Exception:
                errors.append('%s: impossible to retrieve file "%s"' % (
                    default_code, image_path)
                )
                continue

        product = self.env[self.product_model].search([
            ('default_code', '=', default_code)
        ])

        image_name = image_path[image_path.rfind("/")+1:]
        vals = {
            'data': image_base64,
            'name': image_name,
            'file_type': 'image',
            'backend_id': 1, #TODO not hardcode the backend_id
        }

        file_id = file_obj.create(vals)
        tag_id = get_tag(tag_name)
        image = image_obj.create({
            'file_id': file_id.id,
            'name': image_name,
            'alt_name': image_name,
        })

        if self.overwrite:
            domain = [
                ('image_id.name', '=', image.name),
                ('tag_id', '=', tag_id),
                ('product_tmpl_id', '=', product.id),
            ]
            relation_obj.search(domain).unlink()

        if self.product_model == 'product.template' and product:
            relation_obj.create({
                'image_id': image.id,
                'tag_id': tag_id,
                'product_tmpl_id': product.id,
            })
        elif self.product_model == 'product.product' and product:
            relation_obj.create({
                'image_id': image.id,
                'tag_id': tag_id,
                'product_tmpl_id': product.product_tmpl_id.id,
            })
        elif not product:
            errors.append("Could not find the product '%s'" % default_code)

        if errors:
            raise Warning('\n'.join(errors))
