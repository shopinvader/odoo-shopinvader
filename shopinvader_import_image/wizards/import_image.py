# Copyright 2018 Akretion (http://www.akretion.com).
# Author: Sylvain Calador (<https://www.akretion.com>)
# Author: Saritha Sahadevan (<https://www.cybrosys.com>)
# Copyright 2020 Camptocamp (http://www.camptocamp.com)
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import base64
import csv
import io
import logging
import os
import sys
from contextlib import closing
from urllib.request import urlopen
from zipfile import ZipFile

from odoo import _, api, exceptions, fields, models
from odoo.tools.pycompat import csv_reader

_logger = logging.getLogger(__name__)

try:
    import validators
    import magic
except (ImportError, IOError) as err:
    _logger.debug(err)


class ProductImageImportWizard(models.TransientModel):

    _name = "shopinvader.import.product_image"
    _description = "Wizard to import product images"

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
    file_csv = fields.Binary(string="CSV file", required=True)
    csv_header = fields.Char(
        string="CSV file header",
        default="default_code,tag,path",
        required=True,
    )
    csv_delimiter = fields.Char(
        string="CSV file delimiter", default=",", required=True
    )
    source_zipfile = fields.Binary("ZIP with images", required=False)
    options = fields.Serialized(readonly=True)
    overwrite = fields.Boolean(
        "Overwrite image with same name", sparse="options", default=False
    )
    create_missing_tags = fields.Boolean(sparse="options", default=False)
    report = fields.Serialized(readonly=True)
    # FIXME: the report it's computed but is not displayed :/
    report_html = fields.Html(readonly=True, compute="_compute_report_html")

    @api.depends("report")
    def _compute_report_html(self):
        for record in self:
            if not record.report:
                record.report_html = ""
                continue
            report_html = (
                "<div>"
                + "\n".join(
                    [
                        "<p><strong>{}</strong></p><p>{}</p>".format(
                            key, ", ".join(vals)
                        )
                        for key, vals in record.report.items()
                    ]
                )
                + "</div>"
            )
            record.report_html = report_html

    @api.model
    def _get_base64(self, file_path):
        res = {}
        binary = None
        mimetype = None
        if validators.url(file_path):
            binary = self._read_from_url(file_path)
        elif self.source_zipfile:
            binary = self._read_from_zip(file_path)
        if binary:
            mimetype = magic.from_buffer(binary, mime=True)
            res = {"mimetype": mimetype, "b64": base64.encodestring(binary)}
        return res

    def _read_from_url(self, file_path):
        return urlopen(file_path).read()

    def _read_from_zip(self, file_path):
        if not self.source_zipfile:
            raise exceptions.UserError(_("No zip file provided!"))
        file_content = base64.b64decode(self.source_zipfile)
        with closing(io.BytesIO(file_content)) as zip_file:
            with ZipFile(zip_file, "r") as z:
                try:
                    return z.read(file_path)
                except KeyError:
                    # File missing
                    return None

    def _get_lines(self):
        lines = []
        file_content = base64.b64decode(self.file_csv)
        with closing(io.BytesIO(file_content)) as file_csv:
            reader = csv_reader(file_csv, delimiter=self.csv_delimiter)
            headers = next(reader, None)

            if headers != self.csv_header.split(self.csv_delimiter):
                raise exceptions.UserError(
                    _("Invalid CSV file headers found! Expected: %s")
                    % self.csv_header
                )
            csv.field_size_limit(sys.maxsize)

            for row in reader:
                if not row:
                    continue
                default_code, tag_name, file_path = row
                lines.append(
                    {
                        "default_code": default_code,
                        "tag_name": tag_name,
                        "file_path": file_path,
                    }
                )
        return lines

    def _get_options(self):
        return self.options

    def do_import(self):
        self.report = self.report_html = False
        lines = self._get_lines()
        report = self._do_import(
            lines, self.product_model, options=self._get_options()
        )
        self.report = report
        return {"type": "ir.actions.act_view_reload"}

    def _do_import(self, lines, product_model, options=None):
        tag_obj = self.env["image.tag"]
        image_obj = self.env["storage.image"]
        relation_obj = self.env["product.image.relation"]

        report = {
            "created": set(),
            "file_not_found": set(),
            "missing_tags": [],
        }
        options = options or {}

        # do all query at once
        lines_by_code = {x["default_code"]: x for x in lines}
        all_codes = list(lines_by_code.keys())
        _fields = ["default_code", "product_tmpl_id"]
        if product_model == "product.template":
            # exclude template id
            _fields = _fields[:1]

        products = self.env[product_model].search_read(
            [("default_code", "in", all_codes)], _fields
        )
        existing_by_code = {x["default_code"]: x for x in products}
        report["missing"] = sorted(
            [code for code in all_codes if not existing_by_code.get(code)]
        )

        all_tags = [x["tag_name"] for x in lines if x["tag_name"]]
        tags = tag_obj.search_read([("name", "in", all_tags)], ["name"])
        tag_by_name = {x["name"]: x["id"] for x in tags}
        missing_tags = set(all_tags).difference(set(tag_by_name.keys()))
        if missing_tags:
            if options.get("create_missing_tags"):
                for tag_name in missing_tags:
                    tag_by_name[tag_name] = tag_obj.create(
                        {"name": tag_name}
                    ).id
            else:
                report["missing_tags"] = sorted(missing_tags)

        for prod in products:
            line = lines_by_code[prod["default_code"]]
            file_path = line["file_path"]
            file_vals = self._prepare_file_values(file_path)
            if not file_vals:
                report["file_not_found"].add(prod["default_code"])
                continue
            file_vals.update(
                {"name": file_vals["name"], "alt_name": file_vals["name"]}
            )
            # storage_file = file_obj.create(file_vals)
            tag_id = tag_by_name.get(line["tag_name"])

            image = image_obj.create(file_vals)
            if options.get("overwrite"):
                domain = [
                    ("image_id.name", "=", image.name),
                    ("tag_id", "=", tag_id),
                    ("product_tmpl_id", "=", prod["id"]),
                ]
                relation_obj.search(domain).unlink()

            if product_model == "product.template":
                tmpl_id = prod["id"]
            elif product_model == "product.product":
                tmpl_id = prod["product_tmpl_id"]

            relation_obj.create(
                {
                    "image_id": image.id,
                    "tag_id": tag_id,
                    "product_tmpl_id": tmpl_id,
                }
            )
            report["created"].add(prod["default_code"])
        report["created"] = sorted(report["created"])
        report["file_not_found"] = sorted(report["file_not_found"])
        return report

    def _prepare_file_values(self, file_path, filetype="image"):
        name = os.path.basename(file_path)
        file_data = self._get_base64(file_path)
        if not file_data:
            return {}
        vals = {
            "data": file_data["b64"],
            "name": name,
            "file_type": filetype,
            "mimetype": file_data["mimetype"],
            "backend_id": self.storage_backend_id.id,
        }
        return vals
