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
from odoo.tools import date_utils

_logger = logging.getLogger(__name__)

try:
    import magic
    import validators
except (ImportError, IOError) as err:
    _logger.debug(err)


def gen_chunks(iterable, chunksize=10):
    """Chunk generator.

    Take an iterable and yield `chunksize` sized slices.
    "Borrowed" from connector_importer.
    """
    chunk = []
    last_chunk = False
    for i, line in enumerate(iterable):
        if i % chunksize == 0 and i > 0:
            yield chunk, last_chunk
            del chunk[:]
        chunk.append(line)
    last_chunk = True
    yield chunk, last_chunk


class ProductImageImportWizard(models.Model):

    _name = "shopinvader.import.product_image"
    _description = "Handle import of shopinvader product images"

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
    source_type = fields.Selection(
        [
            ("url", "URL"),
            ("zip_file", "Zip file"),
            ("external_storage", "External storage"),
        ],
        string="Source type",
        required=True,
        default="url",
    )
    filename = fields.Char()
    file_csv = fields.Binary(string="CSV file", required=True)
    csv_delimiter = fields.Char(
        string="CSV file delimiter", default=",", required=True,
    )
    csv_column_default_code = fields.Char(
        string="Product Reference column",
        help="The CSV File column name that holds the product reference.",
        default="default_code",
        required=True,
    )
    csv_column_tag_name = fields.Char(
        string="Image Tag Name column",
        help="The CSV File column name that holds the image tag name.",
        default="tag",
        required=True,
    )
    csv_column_file_path = fields.Char(
        string="Image file path column",
        help="The CSV File column name that holds the image file path or url.",
        default="path",
        required=True,
    )
    source_zipfile = fields.Binary("ZIP with images", required=False)
    source_storage_backend_id = fields.Many2one(
        "storage.backend", "Storage Backend with images"
    )
    external_csv_path = fields.Char(
        string="Path to CSV file",
        help="Relative path of the CSV file located in the external storage",
    )
    options = fields.Serialized(readonly=True)
    overwrite = fields.Boolean(
        "Overwrite image with same name", sparse="options", default=False
    )
    create_missing_tags = fields.Boolean(sparse="options", default=False)
    chunk_size = fields.Integer(
        sparse="options",
        default=10,
        help="How many lines will be handled in each job.",
    )
    report = fields.Serialized(readonly=True)
    report_html = fields.Html(readonly=True, compute="_compute_report_html")
    state = fields.Selection(
        [("new", "New"), ("scheduled", "Scheduled"), ("done", "Done")],
        string="Import state",
        default="new",
    )
    done_on = fields.Datetime()

    @api.depends("report")
    def _compute_report_html(self):
        tmpl = self.env.ref("shopinvader_import_image.report_html")
        for record in self:
            if not record.report:
                record.report_html = ""
                continue
            report_html = tmpl.render({"record": record})
            record.report_html = report_html

    @api.model
    def _get_base64(self, file_path):
        res = {}
        binary = None
        mimetype = None
        binary = getattr(self, "_read_from_" + self.source_type)(file_path)
        if binary:
            mimetype = magic.from_buffer(binary, mime=True)
            res = {"mimetype": mimetype, "b64": base64.encodestring(binary)}
        return res

    def _read_from_url(self, file_path):
        if validators.url(file_path):
            return urlopen(file_path).read()
        return None

    def _read_from_zip_file(self, file_path):
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

    def _read_from_external_storage(self, file_path):
        if not self.source_storage_backend_id:
            raise exceptions.UserError(_("No storage backend provided!"))
        return self.source_storage_backend_id._get_bin_data(file_path)

    def _read_csv(self):
        if self.file_csv:
            return base64.b64decode(self.file_csv)
        elif self.external_csv_path:
            return self.source_storage_backend_id._get_bin_data(
                self.external_csv_path
            )

    def _get_lines(self):
        lines = []
        mapping = {
            "default_code": self.csv_column_default_code,
            "tag_name": self.csv_column_tag_name,
            "file_path": self.csv_column_file_path,
        }
        with closing(io.BytesIO(self._read_csv())) as binary_file:
            csv_file = (line.decode("utf8") for line in binary_file)
            reader = csv.DictReader(csv_file, delimiter=self.csv_delimiter)
            csv.field_size_limit(sys.maxsize)
            for row in reader:
                try:
                    line = {
                        key: row[column] for key, column in mapping.items()
                    }
                except KeyError as e:
                    _logger.error(e)
                    raise exceptions.UserError(_("CSV Schema Incompatible"))
                lines.append(line)
        return lines

    def _get_options(self):
        return self.options or {}

    def action_import(self):
        self.report = self.report_html = False
        self.state = "scheduled"
        # Generate N chunks to split in several jobs.
        chunks = gen_chunks(
            self._get_lines(), chunksize=self._get_options().get("chunk_size")
        )
        for i, (chunk, is_last_chunk) in enumerate(chunks, 1):
            self.with_delay().do_import(lines=chunk, last_chunk=is_last_chunk)
            _logger.info(
                "Generated job for chunk nr %d. Is last: %s.",
                i,
                "yes" if is_last_chunk else "no",
            )

    def do_import(self, lines=None, last_chunk=False):
        lines = lines or self._get_lines()
        report = self._do_import(
            lines, self.product_model, options=self._get_options()
        )
        # Refresh report
        extendable_keys = [
            "created",
            "file_not_found",
            "missing",
            "missing_tags",
        ]
        prev_report = self.report or {}
        for k, v in report.items():
            if k in extendable_keys and prev_report.get(k):
                report[k] = sorted(set(prev_report[k] + v))

        # Lock as writing can come from several jobs
        sql = "SELECT id FROM %s WHERE ID IN %%s FOR UPDATE" % self._table
        self.env.cr.execute(sql, (tuple(self.ids),), log_exceptions=False)
        self.write(
            {
                "report": report,
                "state": "done" if last_chunk else self.state,
                "done_on": fields.Datetime.now() if last_chunk else False,
            }
        )
        return report

    def _do_import(self, lines, product_model, options=None):
        tag_obj = self.env["image.tag"]
        image_obj = self.env["storage.image"]
        relation_obj = self.env["product.image.relation"]
        prod_tmpl_attr_value_obj = self.env["product.template.attribute.value"]

        report = {
            "created": set(),
            "file_not_found": set(),
            "missing": [],
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
        else:
            _fields.append("product_template_attribute_value_ids")

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

            if product_model == "product.template":
                tmpl_id = prod["id"]
            elif product_model == "product.product":
                # TODO: test product.product import
                tmpl_id = prod["product_tmpl_id"][0]

            image = image_obj.create(file_vals)
            if options.get("overwrite"):
                domain = [
                    ("image_id.name", "=", image.name),
                    ("tag_id", "=", tag_id),
                    ("product_tmpl_id", "=", tmpl_id),
                ]
                relation_obj.search(domain).unlink()

            img_relation_values = {
                "image_id": image.id,
                "tag_id": tag_id,
                "product_tmpl_id": tmpl_id,
            }
            # Assign specific product attribute values
            if (
                product_model == "product.product"
                and prod["product_template_attribute_value_ids"]
            ):
                attr_values = prod_tmpl_attr_value_obj.browse(
                    prod["product_template_attribute_value_ids"]
                )
                img_relation_values["attribute_value_ids"] = [
                    (
                        6,
                        0,
                        attr_values.mapped("product_attribute_value_id").ids,
                    )
                ]
            relation_obj.create(img_relation_values)
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

    @api.model
    def _cron_cleanup_obsolete(self, days=7):
        from_date = fields.Datetime.now().replace(
            hour=23, minute=59, second=59
        )
        limit_date = date_utils.subtract(from_date, days)
        records = self.search(
            [("state", "=", "done"), ("done_on", "<=", limit_date)]
        )
        records.unlink()
        _logger.info(
            "Cleanup obsolete images import. %d records found.", len(records)
        )

    def _report_label_for(self, key):
        labels = {
            "created": _("Created"),
            "file_not_found": _("Image file not found"),
            "missing": _("Product not found"),
            "missing_tags": _("Tags not found"),
        }
        return labels.get(key, key)
