# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections.abc import Callable
from typing import Any, TypeAlias

from odoo import api, fields, models

# We use AccessDenied instead of AccessError because AccessError is treated
# differently for cache management in tests:
# (https://github.com/odoo/odoo/blob/18.0/odoo/tests/common.py#L487-L492)
from odoo.exceptions import AccessDenied, MissingError
from odoo.http import content_disposition
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval, time

from .virtual_model import VirtualModel

Record: TypeAlias = models.Model


class ShopinvaderRouterHelper(VirtualModel):
    _name = "shopinvader.router.helper"
    _description = "Shopinvader Router Helper"

    # To use get / search / search_count / create / write / unlink methods,
    # you must define a _model attribute containing the model name
    # and a _domain attribute domain that defines the accessible subset of
    # records
    _model = None

    # Common used fields in fastapi endpoints:

    endpoint_id = fields.Many2one(
        "fastapi.endpoint",
        string="Current Endpoint",
        compute="_compute_endpoint_id",
    )
    app = fields.Selection(
        string="Current App",
        related="endpoint_id.app",
    )

    @api.depends_context("fastapi_endpoint_id")
    def _compute_endpoint_id(self):
        for rec in self:
            endpoint_id = rec.env.context.get("fastapi_endpoint_id")
            rec.endpoint_id = rec.env["fastapi.endpoint"].browse(endpoint_id)

    @property
    def model(self):
        if self._model is None:
            raise NotImplementedError(
                self.env._(
                    "Model not defined, you must define a _model attribute on "
                    "your helper to use crud methods"
                )
            )
        return self.env[self._model]

    @property
    def domain(self):
        if getattr(self, "_domain", None) is None:
            raise NotImplementedError(
                self.env._(
                    "Base domain not defined, you must define a _domain "
                    "method on your helper to use crud methods"
                )
            )
        return self._domain()

    def get(self, record_id: int, raise_on_missing: bool = True):
        self.model.check_access("read")
        record = self.model.browse(record_id).filtered_domain(self.domain)
        if raise_on_missing and not record:
            raise MissingError(
                self.env._("{model_name}({record_id}) not found").format(
                    model_name=self.model._name, record_id=record_id
                )
            )
        return record

    def search(self, domain: list = None) -> Record:
        domain = expression.AND([self.domain, domain or []])
        return self.model.search(domain)

    def search_with_count(
        self, domain: list = None, limit=None, offset=None
    ) -> tuple[int, Record]:
        domain = expression.AND([self.domain, domain or []])
        count = self.model.search_count(domain)
        return count, self.model.search(domain, limit=limit, offset=offset)

    def _prepare_values(self, values: Any) -> dict:
        return values

    def _prepare_create_values(self, values: Any) -> dict:
        return self._prepare_values(values)

    def create(self, values: Any) -> Record:  # pylint: disable=method-required-super
        self.model.check_access("create")
        record = (
            self.model.sudo().create(self._prepare_create_values(values)).sudo(False)
        )
        if not self.get(record.id, False):
            raise AccessDenied(
                self.env._(
                    "Cannot create {model_name}(), "
                    "the record would be outside the domain"
                ).format(model_name=self.model._name)
            )
        return record

    def _prepare_write_values(self, values: Any, record: Record) -> dict:
        return self._prepare_values(values)

    def write(self, record_id: int, values: dict) -> Record:  # pylint: disable=method-required-super
        self.model.check_access("write")
        record = self.get(record_id)
        record.sudo().write(self._prepare_write_values(values, record))
        if not self.get(record.id, False):
            raise AccessDenied(
                self.env._(
                    "Cannot write {model_name}({record_id}), "
                    "the record would be outside the domain"
                ).format(model_name=self.model._name, record_id=record_id)
            )
        return record

    def unlink(  # pylint: disable=method-required-super
        self, record_id: int, deletion_info_callback: Callable | None = None
    ) -> None:
        self.model.check_access("unlink")
        record = self.get(record_id)
        # We need to extract information about the record before it is deleted
        rv = deletion_info_callback(record) if deletion_info_callback else None
        record.sudo().unlink()
        return rv

    def generate_report(self, record_id: int, report_name: str) -> tuple[str, bytes]:
        record = self.get(record_id)
        report = self.env["ir.actions.report"]._get_report(report_name)
        content, ext = report._render(report, record.ids)
        report_name = report.name
        if report.print_report_name:
            report_name = safe_eval(
                report.print_report_name, {"object": record, "time": time}
            )

        return f"{report_name}.{ext}", content

    def send_file(self, file, filename, mime_type):
        try:
            from fastapi.responses import StreamingResponse
        except ImportError as e:
            raise NotImplementedError(
                self.env._("send_file is fastapi specific and fastapi is not available")
            ) from e

        header = {
            "Content-Disposition": content_disposition(filename),
        }

        def pseudo_stream():
            yield file

        return StreamingResponse(pseudo_stream(), headers=header, media_type=mime_type)
