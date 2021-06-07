# Copyright 2017 ACSONE SA/NV
# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ShopinvaderVariantBindingWizard(models.TransientModel):

    _name = "shopinvader.variant.binding.wizard"
    _description = "Wizard to bind products to a shopinvader catalogue"

    backend_id = fields.Many2one(
        string="ShopInvader Backend",
        comodel_name="shopinvader.backend",
        required=True,
        ondelete="cascade",
    )
    product_ids = fields.Many2many(
        string="Products", comodel_name="product.product", ondelete="cascade"
    )
    lang_ids = fields.Many2many(
        string="Langs",
        comodel_name="res.lang",
        ondelete="cascade",
        help="List of langs for which a binding must exists. If not "
        "specified, the list of langs defined on the backend is used.",
    )
    run_immediately = fields.Boolean(help="Do not schedule jobs.")

    @api.model
    def default_get(self, fields_list):
        res = super(ShopinvaderVariantBindingWizard, self).default_get(fields_list)
        backend_id = self.env.context.get("active_id", False)
        if backend_id:
            backend = self.env["shopinvader.backend"].browse(backend_id)
            res["backend_id"] = backend_id
            res["lang_ids"] = [(6, None, backend.lang_ids.ids)]
        return res

    def bind_products(self):
        for wizard in self:
            backend = wizard.backend_id
            method = backend.with_delay().bind_selected_products
            run_immediately = wizard.run_immediately or self.env.context.get(
                "bind_products_immediately"
            )
            if run_immediately:
                method = backend.bind_selected_products
            method(
                wizard.product_ids,
                langs=wizard.lang_ids,
                run_immediately=run_immediately,
            )

    @api.model
    def bind_langs(self, backend, lang_ids):
        """Ensure that a shopinvader.variant exists for each lang_id.

        If not, create a new binding for the missing lang. This method is useful
        to ensure that when a lang is added to a backend, all the binding
        for this lang are created for the existing bound products.

        :param backend: backend record
        :param lang_ids: list of lang ids we must ensure that a binding exists
        :return:
        """
        bound_products = self.env["product.product"].search(
            [("shopinvader_bind_ids.backend_id", "=", backend.id)]
        )
        # use in memory record to avoid the creation of useless records into
        # the database
        # by default the wizard check if a product is already bound so we
        # can use it by giving the list of product already bound in one of
        # the specified lang and the process will create the missing one.

        # TODO 'new({})' doesn't work into V13 -> should use model lassmethod
        wiz = self.create(
            {
                "lang_ids": self.env["res.lang"].browse(lang_ids),
                "backend_id": backend.id,
                "product_ids": bound_products,
            }
        )
        wiz.bind_products()
