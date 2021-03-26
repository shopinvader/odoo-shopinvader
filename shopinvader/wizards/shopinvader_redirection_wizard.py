# -*- coding: utf-8 -*-
# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class ShopinvaderRedirection(models.TransientModel):
    _name = "shopinvader.redirection.wizard"

    dest_product_id = fields.Many2one(
        "product.template", "Redirect to Product"
    )
    dest_categ_id = fields.Many2one("product.category", "Redirect to Category")

    def apply_redirection(self):
        if self._context.get("active_model") == "product.category":
            return self._redirect_category()
        elif self._context.get("active_model") == "product.template":
            return self._redirect_product()

    def _redirect_record_to(self, records, dest_record):
        if dest_record in records:
            raise UserError(_(u"You can not redirect a record on itself"))
        for record in records:
            for binding in record.shopinvader_bind_ids:
                dest_binding = dest_record.shopinvader_bind_ids.filtered(
                    lambda s: s.backend_id == binding.backend_id
                    and s.lang_id == binding.lang_id
                )
                if not dest_binding:
                    raise UserError(
                        _(
                            u"The destination record do not have binding for "
                            u"the backend {}"
                        ).format(binding.backend_id.name)
                    )
                binding.url_url_ids.write(
                    {
                        "redirect": True,
                        "model_id": "{},{}".format(
                            dest_binding._name, dest_binding.id
                        ),
                    }
                )
                binding.refresh()
                binding.active = False

    def _redirect_category(self):
        categ_ids = self._context["active_ids"]
        products = self.env["product.template"].search(
            [("categ_id", "=", categ_ids)]
        )
        products.write({"categ_id": self.dest_categ_id.id})
        categs = self.env["product.category"].browse(categ_ids)
        self._redirect_record_to(categs, self.dest_categ_id)
        return True

    def _redirect_product(self):
        self._redirect_record_to(
            self.env["product.template"].browse(self._context["active_ids"]),
            self.dest_product_id,
        )
        return True
