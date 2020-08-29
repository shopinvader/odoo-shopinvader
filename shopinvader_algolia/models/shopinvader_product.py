# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ShopinvaderProduct(models.Model):
    _inherit = "shopinvader.product"

    hierarchical_categories = fields.Serialized(
        compute="_compute_shopinvader_category",
        string="Hierarchical Categories",
    )

    def _compute_shopinvader_category(self):
        super(ShopinvaderProduct, self)._compute_shopinvader_category()

        def get_full_name(categ):
            result = []
            while categ:
                result.insert(0, categ.name)
                categ = categ.parent_id
            return " > ".join(result)

        for record in self:
            hierarchical_categories = {}
            for categ in record.shopinvader_categ_ids:
                hierarchical_categories["lvl%s" % categ.level] = get_full_name(
                    categ.record_id
                )
            record.hierarchical_categories = hierarchical_categories

    @api.model
    def _get_facetting_values(self, se_bakend, lang):
        default = [
            "categories.id",
            "Categories.lvl0hierarchical",
            "Categories.lvl1hierarchical",
            "Categories.lvl2hierarchical",
            "main",
            "redirect_url_key",
            "url_key",
            "sku",
            "price.default.value",
        ]
        # Search backend via search engine backend
        invader_backend = self.env["shopinvader.backend"].search(
            [("se_backend_id", "=", se_bakend.id)], limit=1
        )
        # Product attributes do not have a unique code to reference them.
        # In the index data, the attributes are exported per each lang
        # using the translated name, eg:
        # `variant_attributes.model` for English
        # `variant_attributes.modele` for French
        # which means there's no unique key to search for in the search engine.
        # As a workaround, let's make sure that facet filters use the right one.
        # TODO: in the long term it would be better to have a unique name
        # for every filter/attribute
        # to unify them in indexes and Locomotive settings.
        filters = invader_backend.with_context(lang=lang.code).filter_ids
        filter_facetting_values = [f.display_name for f in filters]
        return default + filter_facetting_values
