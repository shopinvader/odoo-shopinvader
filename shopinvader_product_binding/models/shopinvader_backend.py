# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, fields, models


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    nbr_product = fields.Integer(
        compute="_compute_nbr_content", string="Number of bound products"
    )
    nbr_variant = fields.Integer(compute="_compute_nbr_content")
    nbr_category = fields.Integer(compute="_compute_nbr_content")
    use_shopinvader_product_name = fields.Boolean(
        string="Use Shopinvader product display name",
        help="If checked, use the specific shopinvader display name for "
        "products instead of the original product name.",
    )
    category_root_binding_level = fields.Integer(
        default=0,
        help="Define the starting level for root categories when auto-binding."
        "This is typically handy when you want to have some root categories "
        "for internal organization only (eg: All / Saleable) "
        "but you don't want them to appear in the shop."
        "Works for both 'Bind all products' and 'Bind all categories'",
    )
    category_binding_level = fields.Integer(
        default=0,
        help="Define if the product binding should also bind related "
        "categories and how many related parents.\n"
        "Set 0 (or less) to disable the category auto-binding.\n"
        "Set 1 to auto-bind the direct category.\n"
        "Set 2 to auto-bind the direct category and his parent.\n"
        "etc.",
    )
    filter_ids = fields.Many2many(comodel_name="product.filter", string="Filter")
    
    @api.model
    def _to_compute_nbr_content(self):
        """
        Get a dict to compute the number of content.
        The dict is build like this:
        Key = Odoo number fields string (should be Integer/Float)
        Value = The target model string
        :return: dict
        """
        values = {
            # key => Odoo field: value => related model
            "nbr_product": "shopinvader.product",
            "nbr_category": "shopinvader.category",
            "nbr_variant": "shopinvader.variant",
        }
        return values

    def _compute_nbr_content(self):
        to_count = self._to_compute_nbr_content()
        domain = [("backend_id", "in", self.ids)]
        for odoo_field, odoo_model in to_count.items():
            if odoo_model in self.env and self.env[odoo_model]._is_an_ordinary_table():
                target_model_obj = self.env[odoo_model]
                result = target_model_obj.read_group(
                    domain, ["backend_id"], ["backend_id"], lazy=False
                )
                result = {data["backend_id"][0]: data["__count"] for data in result}
                for record in self:
                    record[odoo_field] = result.get(record.id, 0)

    def _bind_all_content(self, model, bind_model, domain, langs="all"):
        assert langs in ("all", "none")
        _langs = self.lang_ids if langs == "all" else self.lang_ids.browse()

        bind_model_obj = self.env[bind_model].with_context(active_test=False)
        model_obj = self.env[model]
        records = model_obj.search(domain)
        binding_domain = [
            ("backend_id", "in", self.ids),
            ("record_id", "in", records.ids),
        ]
        if _langs:
            binding_domain.append(("lang_id", "in", _langs.ids))
        bindings = bind_model_obj.search(binding_domain)
        for backend in self:
            # Loop on langs or on empty lang if lang-agnostic
            for lang in _langs or [_langs]:
                for record in records:
                    backend._get_or_create_existing_binding_for_record(
                        record, bindings, lang=lang
                    )
        return True

    def _get_or_create_existing_binding_for_record(self, record, bindings, lang=False):
        domain = [
            ("backend_id", "=", self.id),
            ("record_id", "=", record.id),
        ]
        if lang:
            domain.append(("lang_id", "=", lang.id))
        binding = fields.first(bindings.filtered_domain(domain))
        if not binding:
            values = {
                "backend_id": self.id,
                "record_id": record.id,
            }
            if lang:
                values["lang_id"] = lang.id
            values_handler = getattr(
                bindings, "_binding_create_values_get", lambda vals: vals
            )
            binding = bindings.with_context(map_children=True).create(
                values_handler(values)
            )
        elif not binding.active:
            binding.write({"active": True})
        return binding

    def bind_all_product(self, domain=None):
        domain = domain or [("sale_ok", "=", True)]
        result = self._bind_all_content(
            "product.template", "shopinvader.product", domain
        )
        self.auto_bind_categories()
        return result

    def auto_bind_categories(self):
        """
        Auto bind product.category for bound shopinvader.product
        :return: bool
        """
        backends = self.filtered(lambda b: b.category_binding_level > 0)
        if not backends:
            return True
        all_products = self.env["shopinvader.variant"].search(
            [
                ("backend_id", "in", backends.ids),
                # Force to have only active binding
                ("active", "=", True),
            ]
        )
        for backend in backends:
            shopinv_variants = all_products.filtered(lambda p: p.backend_id == backend)
            products = shopinv_variants.mapped("record_id")
            categories = backend._get_related_categories(products)
            if categories:
                self._bind_all_content(
                    categories._name,
                    "shopinvader.category",
                    [("id", "in", categories.ids)],
                )
        return True

    def _get_related_categories(self, products):
        """Get related product.category to bind based on current backend.

        :param products: product recordset (product or template)
        :return: product.category recordset
        """
        self.ensure_one()
        # As we consume the first level (direct category), minus 1
        level = self.category_binding_level - 1
        # TODO: this will include categories out of the level of hierarchy
        # when they are assigned directly to the product.
        # We should have a flag to turn this on/off explicitely
        # and in case it should documented on the backend UI.
        categories = products.mapped("categ_id")
        # pull up until the correct level
        parent_categories = categories
        while level > 0:
            parent_categories = parent_categories.mapped("parent_id")
            categories |= parent_categories
            level -= 1
        to_exclude = self._get_categories_to_exclude()
        return categories - to_exclude

    def _get_categories_to_exclude(self):
        root_lvl = self.category_root_binding_level
        if not root_lvl:
            return self.env["product.category"].browse()
        categories = self.env["product.category"].search([("parent_id", "=", False)])
        lvl = root_lvl - 1  # the limit is inclusive
        while lvl:
            categories += categories.mapped("child_id")
            lvl -= 1
        return categories

    def bind_all_category(self, domain=None):
        if domain is None:
            domain = []
            to_exclude = self._get_categories_to_exclude()
            if to_exclude:
                domain = [("id", "not in", to_exclude.ids)]
        # TODO: we should exclude levels from `category_binding_level` as well
        self._bind_all_content("product.category", "shopinvader.category", domain)

    def bind_selected_products(self, products, langs=None, run_immediately=False):
        """Bind given product variants.

        :param products: product.product recordset
        :param langs: res.lang recordset. If none, all langs from backend
        :param run_immediately: do not use jobs
        """
        for backend in self:
            langs = langs or backend.lang_ids
            grouped_by_template = defaultdict(self.env["product.product"].browse)
            for rec in products:
                grouped_by_template[rec.product_tmpl_id] |= rec
            for tmpl, variants in grouped_by_template.items():
                if run_immediately:
                    backend.bind_single_product(langs, tmpl, variants)
                else:
                    backend.with_delay().bind_single_product(langs, tmpl, variants)

    def bind_single_product(self, langs, product_tmpl, variants):
        """Bind given product variants for given template and languages.

        :param langs: res.lang recordset
        :param product_tmpl: product.template browse record
        :param variants: product.product recordset
        :param run_immediately: do not use jobs
        """
        self.ensure_one()
        shopinvader_products = self._get_or_create_shopinvader_products(
            langs, product_tmpl
        )
        for shopinvader_product in shopinvader_products:
            self._get_or_create_shopinvader_variants(shopinvader_product, variants)
        self.auto_bind_categories()

    def _get_or_create_shopinvader_products(self, langs, product_tmpl):
        """Get template bindings for given languages or create if missing.

        :param langs: res.lang recordset
        :param product_tmpl: product.template browse record
        """
        binding_model = self.env["shopinvader.product"].with_context(active_test=False)
        bound_templates = binding_model.search(
            [
                ("record_id", "=", product_tmpl.id),
                ("backend_id", "=", self.id),
                ("lang_id", "in", langs.ids),
            ]
        )
        for lang in langs:
            shopinvader_product = bound_templates.filtered(lambda x: x.lang_id == lang)
            if not shopinvader_product:
                # fmt: off
                data = {
                    "record_id": product_tmpl.id,
                    "backend_id": self.id,
                    "lang_id": lang.id,
                }
                # fmt: on
                bound_templates |= binding_model.create(data)
            elif not shopinvader_product.active:
                shopinvader_product.write({"active": True})
        return bound_templates

    def _get_or_create_shopinvader_variants(self, shopinvader_product, variants):
        """Get variant bindings, create if missing.

        :param langs: res.lang recordset
        :param product_tmpl: product.template browse record
        """
        binding_model = self.env["shopinvader.variant"]
        bound_variants = shopinvader_product.shopinvader_variant_ids
        for variant in variants:
            shopinvader_variant = bound_variants.filtered(
                lambda p: p.record_id == variant
            )
            if not shopinvader_variant:
                # fmt: off
                data = {
                    "record_id": variant.id,
                    "backend_id": self.id,
                    "shopinvader_product_id":
                        shopinvader_product.id,
                }
                # fmt: on
                bound_variants |= binding_model.create(data)
            elif not shopinvader_variant.active:
                shopinvader_variant.write({"active": True})
        return bound_variants
