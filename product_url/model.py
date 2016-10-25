# -*- coding: utf-8 -*-

from openerp import models, api, fields, _


class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = [
        "abstract.url",
        "product.template",
    ]



class UrlUrl(models.Model):
    _inherit = "url.url"

    @api.model
    def _reference_models(self):
        res = super(UrlUrl, self)._reference_models()

        res += [("product.template","Product"), ('product.category', "Category")]
        return res


class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = [
        "abstract.url",
        "product.category",
    ]


