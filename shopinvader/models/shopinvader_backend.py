# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict
from contextlib import contextmanager

from odoo import _, api, fields, models, tools
from odoo.http import request
from odoo.osv import expression

from odoo.addons.base_sparse_field.models.fields import Serialized
from odoo.addons.server_environment import serv_config


class ShopinvaderBackend(models.Model):
    _name = "shopinvader.backend"
    _inherit = [
        "collection.base",
        "server.env.techname.mixin",
        "server.env.mixin",
    ]
    _description = "Shopinvader Backend"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        default=lambda s: s._default_company_id(),
    )
    location = fields.Char()
    notification_ids = fields.One2many(
        "shopinvader.notification",
        "backend_id",
        "Notification",
        default=lambda self: self.env["shopinvader.notification"].search([]),
    )
    nbr_product = fields.Integer(
        compute="_compute_nbr_content", string="Number of bound products"
    )
    nbr_variant = fields.Integer(compute="_compute_nbr_content")
    nbr_category = fields.Integer(compute="_compute_nbr_content")
    nbr_cart = fields.Integer(compute="_compute_nbr_sale_order")
    nbr_sale = fields.Integer(compute="_compute_nbr_sale_order")
    allowed_country_ids = fields.Many2many(
        comodel_name="res.country", string="Allowed Country"
    )
    anonymous_partner_id = fields.Many2one(
        "res.partner",
        "Anonymous Partner",
        help=(
            "Provide partner settings for unlogged users "
            "(i.e. fiscal position)"
        ),
        required=True,
        default=lambda self: self.env.ref("shopinvader.anonymous"),
    )
    sequence_id = fields.Many2one(
        "ir.sequence", "Sequence", help="Naming policy for orders and carts"
    )
    auth_api_key_id = fields.Many2one(
        "auth.api.key",
        "Api Key",
        required=True,
        help="Api_key section used for the authentication of"
        "calls to services dedicated to this backend",
        copy=False,
    )
    lang_ids = fields.Many2many("res.lang", string="Lang", required=True)
    pricelist_id = fields.Many2one(
        "product.pricelist",
        string="Pricelist",
        default=lambda self: self._default_pricelist_id(),
    )
    account_analytic_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic account",
        help="This analytic account will be used to fill the "
        "field on the sale order created.",
    )
    filter_ids = fields.Many2many(
        comodel_name="product.filter", string="Filter"
    )
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
    user_id = fields.Many2one(
        related="auth_api_key_id.user_id",
        readonly=True,
        help="The technical user used to process calls to the services "
        "provided by the backend",
    )
    website_public_name = fields.Char(
        help="Public name of your backend/website.\n"
        " Used for products name referencing."
    )
    clear_cart_options = fields.Selection(
        selection=[
            ("delete", "Delete"),
            ("clear", "Clear"),
            ("cancel", "Cancel"),
        ],
        required=True,
        string="Clear cart",
        default="clear",
        help="Action to execute on the cart when the front want to clear the "
        "current cart:\n"
        "- Delete: delete the cart (and items);\n"
        "- Clear: keep the cart but remove items;\n"
        "- Cancel: The cart is canceled but kept into the database.\n"
        "When a quotation is not validated, habitually it's not removed "
        "but cancelled. "
        "It could be also useful if you want to keep cart for "
        "statistics reasons. A new cart is created automatically when the "
        "customer will add a new item.",
    )
    cart_checkout_address_policy = fields.Selection(
        selection=[
            ("no_defaults", "No defaults"),
            (
                "invoice_defaults_to_shipping",
                "Invoice address defaults to shipping",
            ),
        ],
        default="no_defaults",
        required=True,
        string="Cart address behavior",
        help="Define how the cart address will be handled in the checkout step:\n"
        "- No defaults: client will pass shipping and invoicing address"
        " together or in separated calls."
        " No automatic value for non passed addresses will be set;\n"
        "- Invoice address defaults to shipping:"
        " if the client does not pass the invoice address explicitly "
        " the shipping one will be used as invoice address as well.\n",
    )
    validate_customers = fields.Boolean(
        default=False,  # let's be explicit here :)
        help="Turn on this flag to block non validated customers. "
        "If customers' partners are not validated, "
        "registered users cannot log in. "
        "Salesman will get notified via mail activity.",
    )
    validate_customers_type = fields.Selection(
        selection=[
            ("all", "Companies, simple users and addresses"),
            ("company", "Company users only"),
            ("user", "Simple users only"),
            ("company_and_user", "Companies and simple users"),
            ("address", "Addresses only"),
        ],
        default="all",
    )
    salesman_notify_create = fields.Selection(
        selection=[
            ("", "None"),
            ("all", "Companies, simple users and addresses"),
            ("company", "Company users only"),
            ("user", "Simple users only"),
            ("company_and_user", "Companies and simple users"),
            ("address", "Addresses only"),
        ],
        default="company",
    )
    salesman_notify_update = fields.Selection(
        selection=[
            ("", "None"),
            ("all", "Companies, simple users and addresses"),
            ("company", "Company users only"),
            ("user", "Simple users only"),
            ("company_and_user", "Companies and simple users"),
            ("address", "Addresses only"),
        ],
        default="",
    )
    partner_title_ids = fields.Many2many(
        "res.partner.title",
        string="Available partner titles",
        default=lambda self: self._default_partner_title_ids(),
    )
    partner_industry_ids = fields.Many2many(
        "res.partner.industry",
        string="Available partner industries",
        default=lambda self: self._default_partner_industry_ids(),
    )
    # Sale settings aggregator.
    # Use this for `sparse` attribute of sale related settings
    # that do not require a real field.
    sale_settings = Serialized(
        # Default values on the sparse fields work only for create
        # and does not provide defaults for existing records.
        default={}
    )
    # Invoice settings aggregator.
    # Use this for `sparse` attribute of invoice related settings
    # that do not require a real field.
    invoice_settings = Serialized(
        default={
            "invoice_linked_to_sale_only": True,
            "invoice_access_open": False,
        }
    )
    # TODO: move to portal mode?
    invoice_linked_to_sale_only = fields.Boolean(
        default=True,
        string="Only sale invoices",
        help="Only serve invoices that are linked to a sale order.",
        sparse="invoice_settings",
    )
    invoice_access_open = fields.Boolean(
        default=False,
        string="Open invoices",
        help="Give customer access to open invoices as well as the paid ones.",
        sparse="invoice_settings",
    )
    invoice_report_id = fields.Many2one(
        comodel_name="ir.actions.report",
        domain=lambda self: self._get_invoice_report_id_domain(),
        string="Specific report",
        help="Select a specific report for invoice download, if none are selected "
        "default shopinvader implementation is used.",
    )
    customer_default_role = fields.Char(
        compute="_compute_customer_default_role",
    )

    _sql_constraints = [
        (
            "auth_api_key_id_uniq",
            "unique(auth_api_key_id)",
            "An authentication API Key can be used by only one backend.",
        )
    ]

    @property
    def _server_env_fields(self):
        return {"location": {}}

    @api.model
    def _default_company_id(self):
        return self.env.company

    @api.model
    def _default_pricelist_id(self):
        return self.env.ref("product.list0")

    @api.model
    def _default_partner_title_ids(self):
        return self.env["res.partner.title"].search([])

    @api.model
    def _default_partner_industry_ids(self):
        return self.env["res.partner.industry"].search([])

    def _compute_customer_default_role(self):
        for rec in self:
            rec.customer_default_role = "default"

    def _get_invoice_report_id_domain(self):
        return [
            (
                "binding_model_id",
                "=",
                self.env.ref("account.model_account_move").id,
            )
        ]

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
            if (
                odoo_model in self.env
                and self.env[odoo_model]._is_an_ordinary_table()
            ):
                target_model_obj = self.env[odoo_model]
                result = target_model_obj.read_group(
                    domain, ["backend_id"], ["backend_id"], lazy=False
                )
                result = {
                    data["backend_id"][0]: data["__count"] for data in result
                }
                for record in self:
                    record[odoo_field] = result.get(record.id, 0)

    @api.model
    def _to_compute_nbr_sale_order(self):
        """Get a dict to compute the number of sale order.

        The dict is build like this:
            {field_name: domain}
        """
        return {
            "nbr_cart": [("typology", "=", "cart")],
            "nbr_sale": [("typology", "=", "sale")],
        }

    def _compute_nbr_sale_order(self):
        domain = [("shopinvader_backend_id", "in", self.ids)]
        for fname, fdomain in self._to_compute_nbr_sale_order().items():
            res = self.env["sale.order"].read_group(
                domain=expression.AND([domain, fdomain]),
                fields=["shopinvader_backend_id"],
                groupby=["shopinvader_backend_id"],
                lazy=False,
            )
            counts = {
                r["shopinvader_backend_id"][0]: r["__count"] for r in res
            }
            for rec in self:
                rec[fname] = counts.get(rec.id, 0)

    def _bind_all_content(self, model, bind_model, domain):
        bind_model_obj = self.env[bind_model].with_context(active_test=False)
        model_obj = self.env[model]
        records = model_obj.search(domain)
        binds = bind_model_obj.search(
            [
                ("backend_id", "in", self.ids),
                ("record_id", "in", records.ids),
                ("lang_id", "in", self.mapped("lang_ids").ids),
            ]
        )
        for backend in self:
            for lang in backend.lang_ids:
                for record in records:
                    bind = fields.first(
                        binds.filtered(
                            lambda b: b.backend_id == backend
                            and b.record_id == record
                            and b.lang_id == lang
                        )
                    )
                    if not bind:
                        bind_model_obj.with_context(map_children=True).create(
                            {
                                "backend_id": backend.id,
                                "record_id": record.id,
                                "lang_id": lang.id,
                            }
                        )
                    elif not bind.active:
                        bind.write({"active": True})
        return True

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
            shopinv_variants = all_products.filtered(
                lambda p: p.backend_id == backend
            )
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
        categories = self.env["product.category"].search(
            [("parent_id", "=", False)]
        )
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
        self._bind_all_content(
            "product.category", "shopinvader.category", domain
        )

    def bind_selected_products(
        self, products, langs=None, run_immediately=False
    ):
        """Bind given product variants.

        :param products: product.product recordset
        :param langs: res.lang recordset. If none, all langs from backend
        :param run_immediately: do not use jobs
        """
        for backend in self:
            langs = langs or backend.lang_ids
            grouped_by_template = defaultdict(
                self.env["product.product"].browse
            )
            for rec in products:
                grouped_by_template[rec.product_tmpl_id] |= rec
            method = backend.with_delay().bind_single_product
            if run_immediately:
                method = backend.bind_single_product
            for tmpl, variants in grouped_by_template.items():
                method(langs, tmpl, variants)

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
            self._get_or_create_shopinvader_variants(
                shopinvader_product, variants
            )
        self.auto_bind_categories()

    def _get_or_create_shopinvader_products(self, langs, product_tmpl):
        """Get template bindings for given languages or create if missing.

        :param langs: res.lang recordset
        :param product_tmpl: product.template browse record
        """
        binding_model = self.env["shopinvader.product"].with_context(
            active_test=False
        )
        bound_templates = binding_model.search(
            [
                ("record_id", "=", product_tmpl.id),
                ("backend_id", "=", self.id),
                ("lang_id", "in", langs.ids),
            ]
        )
        for lang in langs:
            shopinvader_product = bound_templates.filtered(
                lambda x: x.lang_id == lang
            )
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

    def _get_or_create_shopinvader_variants(
        self, shopinvader_product, variants
    ):
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

    def _send_notification(self, notification, record):
        self.ensure_one()
        record.ensure_one()
        notifs = self.env["shopinvader.notification"].search(
            [
                ("backend_id", "=", self.id),
                ("notification_type", "=", notification),
            ]
        )
        description = _("Notify %s for %s,%s") % (
            notification,
            record._name,
            record.id,
        )
        for notif in notifs:
            notif.with_delay(description=description).send(record.id)
        return True

    def _extract_configuration(self):
        return {}

    @classmethod
    def _get_api_key_name(cls, auth_api_key):
        for section in serv_config.sections():
            if section.startswith("api_key_") and serv_config.has_option(
                section, "key"
            ):
                if tools.consteq(
                    auth_api_key, serv_config.get(section, "key")
                ):
                    return section
        return None

    @api.model
    @tools.ormcache("self._uid", "auth_api_key_id")
    def _get_id_from_auth_api_key(self, auth_api_key_id):
        return self.search([("auth_api_key_id", "=", auth_api_key_id)]).id

    @api.model
    def _get_from_http_request(self):
        auth_api_key_id = getattr(request, "auth_api_key_id", None)
        return self.browse(self._get_id_from_auth_api_key(auth_api_key_id))

    def _bind_langs(self, lang_ids):
        self.ensure_one()
        self.env["shopinvader.variant.binding.wizard"].bind_langs(
            self, lang_ids
        )
        self.env["shopinvader.category.binding.wizard"].bind_langs(
            self, lang_ids
        )

    def _unbind_langs(self, lang_ids):
        self.ensure_one()
        self.env["shopinvader.variant.unbinding.wizard"].unbind_langs(
            self, lang_ids
        )
        self.env["shopinvader.category.unbinding.wizard"].unbind_langs(
            self, lang_ids
        )

    @contextmanager
    def _keep_binding_sync_with_langs(self):
        lang_ids_by_record = {}
        for record in self:
            lang_ids_by_record[record.id] = record.lang_ids.ids
        yield
        for record in self:
            old_lang_ids = set(lang_ids_by_record[record.id])
            actual_lang_ids = set(record.lang_ids.ids)
            if old_lang_ids == actual_lang_ids:
                continue
            added_lang_ids = actual_lang_ids - old_lang_ids
            if added_lang_ids:
                record._bind_langs(list(added_lang_ids))
            removed_lang_ids = old_lang_ids - actual_lang_ids
            if removed_lang_ids:
                record._unbind_langs(list(removed_lang_ids))

    def write(self, values):
        if "auth_api_key_id" in values:
            self._get_id_from_auth_api_key.clear_cache(self.env[self._name])
        with self._keep_binding_sync_with_langs():
            return super(ShopinvaderBackend, self).write(values)

    def _get_backend_pricelist(self):
        """The pricelist configure by this backend."""
        # There must be a pricelist somehow: safe fallback to default Odoo one
        return self.pricelist_id or self._default_pricelist_id()

    def _get_customer_default_pricelist(self):
        """Retrieve pricelist to be used for brand new customer record.
        """
        return self._get_backend_pricelist()

    def _get_partner_pricelist(self, partner):
        """Retrieve pricelist for given res.partner record.
        """
        # Normally we should return partner.property_product_pricelist
        # but by default the shop must use the same pricelist for all customers
        # because products' prices are computed only by backend pricelist.
        # Nevertheless, this is a good point to hook to
        # if a different behavior per partner is required.
        return None

    def _get_cart_pricelist(self, partner=None):
        """Retrieve pricelist to be used for the cart.

        NOTE: if you change this behavior be aware that
        the prices displayed on the cart might differ
        from the ones showed on product details.
        This is because product info comes from indexes
        which are completely agnostic in regard to specific partner info.
        """
        pricelist = self._get_backend_pricelist()
        if partner:
            pricelist = self._get_partner_pricelist(partner) or pricelist
        return pricelist
