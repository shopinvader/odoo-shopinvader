# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import Annotated

from fastapi import Depends

from odoo import api, fields

from odoo.addons.fastapi.dependencies import odoo_env
from odoo.addons.fastapi.routers import demo_router

from ..virtual_model import VirtualModel


class RouterHelperTestContext(VirtualModel):
    _inherit = "shopinvader.router.helper"
    _name = "shopinvader.router.context_test.helper"
    _description = "Test Context"

    def _get_endpoint_app(self):
        return f"{self.app}/{self.endpoint_id.name}"


class RouterHelperTestBase(VirtualModel):
    _inherit = "shopinvader.router.helper"
    _name = "shopinvader.router.base_test.helper"
    _description = "Test Base"

    name = fields.Char()
    type = fields.Selection(
        selection=[("type_1", "Type 1"), ("type_2", "Type 2")],
        default="type_1",
    )


class RouterHelperTestRelations(VirtualModel):
    _inherit = "shopinvader.router.helper"
    _name = "shopinvader.router.relations_test.helper"
    _description = "Test Relations"

    name = fields.Char()
    partner_id = fields.Many2one("res.partner")
    partner_name = fields.Char("Partner Name", related="partner_id.name")


class RouterHelperTestModelBoundNoDomain(VirtualModel):
    _inherit = "shopinvader.router.helper"
    _name = "shopinvader.router.no_domain_test.helper"
    _description = "Test Model Bound No Domain"

    _model = "res.partner"


class RouterHelperTestModelBound(VirtualModel):
    _inherit = "shopinvader.router.helper"
    _name = "shopinvader.router.model_bound_test.helper"
    _description = "Test Model Bound"

    _model = "res.partner"

    def _domain(self):
        return [("category_id", "in", self.category_ids.ids)]

    category_ids = fields.Many2many(
        "res.partner.category",
        required=True,
        relation="shopinvader_router_model_bound_category_rel",
    )


def endpoint_helper(
    env: Annotated[api.Environment, Depends(odoo_env)],
):
    return env["shopinvader.router.context_test.helper"].new()


# Extend the demo router to have an endpoint that uses the helper and returns
# current app / endpoint
@demo_router.get("/demo/helper")
async def get_endpoint_app(
    helper: Annotated[RouterHelperTestContext, Depends(endpoint_helper)],
) -> str:
    """Returns the helper current app / endpoint"""
    return helper._get_endpoint_app()
