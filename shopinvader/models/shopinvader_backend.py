# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager

from odoo import _, api, fields, models, tools
from odoo.addons.http_routing.models.ir_http import slugify
from odoo.addons.queue_job.job import job
from odoo.addons.server_environment import serv_config
from odoo.http import request
from odoo.osv import expression


class ShopinvaderBackend(models.Model):
    _name = "shopinvader.backend"
    _inherit = ["collection.base", "server.env.mixin"]
    _description = "Shopinvader Backend"

    name = fields.Char(required=True)
    tech_name = fields.Char(
        required=True,
        help="Unique name for technical purposes. " "Eg: server env keys.",
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        default=lambda s: s._default_company_id(),
    )
    location = fields.Char()
    notification_ids = fields.One2many(
        "shopinvader.notification", "backend_id", "Notification"
    )
    nbr_product = fields.Integer(
        compute="_compute_nbr_content", string="Number of binded products"
    )
    nbr_variant = fields.Integer(compute="_compute_nbr_content")
    nbr_category = fields.Integer(compute="_compute_nbr_content")
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
    pricelist_id = fields.Many2one("product.pricelist", string="Pricelist")

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

    _sql_constraints = [
        (
            "auth_api_key_id_uniq",
            "unique(auth_api_key_id)",
            "An authentication API Key can be used by only one backend.",
        ),
        ("tech_name_uniq", "unique(tech_name)", "`tech_name` must be unique"),
    ]

    @property
    def _server_env_fields(self):
        return {"location": {}}

    @api.multi
    def _server_env_section_name(self):
        self.ensure_one()
        if not self.tech_name:
            return
        base = self._server_env_global_section_name()
        return ".".join((base, self.tech_name))

    @api.model
    def _default_company_id(self):
        return self.env["res.company"]._company_default_get(
            "shopinvader.backend"
        )

    @api.model
    def _default_partner_title_ids(self):
        return self.env["res.partner.title"].search([])

    @api.model
    def _default_partner_industry_ids(self):
        return self.env["res.partner.industry"].search([])

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

    @api.multi
    def bind_all_product(self):
        result = self._bind_all_content(
            "product.template", "shopinvader.product", [("sale_ok", "=", True)]
        )
        self.auto_bind_categories()
        return result

    @api.multi
    def auto_bind_categories(self):
        """
        Auto bind product.category for binded shopinvader.product
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

    @api.multi
    def _get_related_categories(self, products):
        """
        Get product.category to bind (based on current backend and
        given products)
        :param products: product recordset (product or template)
        :return: product.category recordset
        """
        self.ensure_one()
        # As we consume the first level (direct category), minus 1
        level = self.category_binding_level - 1
        categories = products.mapped("categ_id")
        # pull up until the correct level
        parent_categories = categories
        while level > 0:
            parent_categories = parent_categories.mapped("parent_id")
            categories |= parent_categories
            level -= 1
        return categories

    @api.multi
    def bind_all_category(self):
        self._bind_all_content("product.category", "shopinvader.category", [])

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

    @api.multi
    def _bind_langs(self, lang_ids):
        self.ensure_one()
        self.env["shopinvader.variant.binding.wizard"].bind_langs(
            self, lang_ids
        )
        self.env["shopinvader.category.binding.wizard"].bind_langs(
            self, lang_ids
        )

    @api.multi
    def _unbind_langs(self, lang_ids):
        self.ensure_one()
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

    @api.multi
    def write(self, values):
        if "auth_api_key_id" in values:
            self._get_id_from_auth_api_key.clear_cache(self.env[self._name])
        with self._keep_binding_sync_with_langs():
            return super(ShopinvaderBackend, self).write(values)

    # TODO: would be nice to put this `tech_name` logic into server.env.mixin
    # as we already copied it from search engine backend.
    @api.model
    def create(self, vals):
        # make sure technical names are always there
        if not vals.get("tech_name"):
            vals["tech_name"] = self._normalize_name(vals["name"])
        return super().create(vals)

    @staticmethod
    def _normalize_name(name):
        return slugify(name).replace("-", "_")

    @api.onchange("name")
    def _onchange_name(self):
        if self.name and not self.tech_name:
            self.tech_name = self._normalize_name(self.name)

    @api.multi
    @job(default_channel="root.shopinvader")
    def _job_sale_price_update(self, sales):
        """
        Jobify the process to update prices.
        After launching the price update, we also have to re-apply promotions
        (in case of the promotion change and conditions doesn't match anymore).
        Could be inherited to add others prices recompute.
        :param sales: sale.order recordset
        :return: None
        """
        sales._update_pricelist_and_update_line_prices()

    @api.multi
    @job(default_channel="root.shopinvader")
    def _job_split_sale_price_update(self, sales):
        """
        Split the current job on many SO to 1 job per SO.
        To avoid rollback full price update in case of error.
        Better to have 1 SO bad recomputed instead of all SO.
        :param sales: sale.order recordset
        :return: bool
        """
        for sale in sales:
            description = "Recompute prices for cart %s" % sale.display_name
            self.with_delay(description=description)._job_sale_price_update(
                sale
            )
        return True

    @api.model
    def _launch_sale_price_update(self, domain=False):
        """
        Retrieve cart to update then apply the recalculation
        (could be used for a cron)
        :param domain: list/domain
        :return: bool
        """
        domain = domain or []
        if domain:
            domain = expression.normalize_domain(domain)
        sale_domain = expression.normalize_domain(
            [("typology", "=", "cart"), ("state", "=", "draft")]
        )
        domain = expression.AND([domain, sale_domain])
        sale_carts = self.env["sale.order"].search(domain)
        if sale_carts:
            description = "Recompute prices for carts (split: 1 job per cart)"
            return self.with_delay(
                description=description
            )._job_split_sale_price_update(sale_carts)
        return True
