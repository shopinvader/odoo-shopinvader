# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _search_shopinvader_backend_ids(self, operator, value):
        si_var_obj = self.env["shopinvader.variant"]
        bindings = si_var_obj.search([("backend_id.name", operator, value)])

        return [("id", "in", bindings.mapped("record_id").ids)]

    shopinvader_bind_ids = fields.One2many(
        "shopinvader.variant",
        "record_id",
        string="Shopinvader Binding",
        context={"active_test": False},
    )

    shopinvader_backend_ids = fields.Many2many(
        string="ShopInvader Backends",
        comodel_name="shopinvader.backend",
        compute="_compute_shopinvader_backend_ids",
        store=False,
        search=_search_shopinvader_backend_ids,
    )
    active = fields.Boolean(inverse="_inverse_active")

    is_shopinvader_binded = fields.Boolean(
        "Shopinvader binded",
        compute="_compute_is_shopinvader_binded",
        store=True,
        index=True,
        help="Technical field to know if this product is related by a"
        "(at least one) shopinvader backend",
    )

    @api.multi
    @api.depends("shopinvader_bind_ids", "shopinvader_bind_ids.backend_id")
    def _compute_is_shopinvader_binded(self):
        """
        Compute function to determine if the product is used in at least
        1 backend (using backend from shopinvader.variant)
        :return:
        """
        for rec in self:
            binded = bool(rec.shopinvader_bind_ids.mapped("backend_id"))
            rec.is_shopinvader_binded = binded

    @api.multi
    def _inverse_active(self):
        self.filtered(lambda p: not p.active).mapped(
            "shopinvader_bind_ids"
        ).write({"active": False})

    @api.multi
    def _compute_shopinvader_backend_ids(self):
        for rec in self:
            rec.shopinvader_backend_ids = rec.mapped(
                "shopinvader_bind_ids.backend_id"
            )

    def unlink(self):
        # Call unlink manually to be sure to trigger
        # shopinvader variant unlink constraint
        self.mapped("shopinvader_bind_ids").unlink()
        return super(ProductProduct, self).unlink()
