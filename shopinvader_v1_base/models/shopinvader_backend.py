# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import hashlib
import os

from odoo import _, api, fields, models, tools
from odoo.osv import expression

from odoo.addons.base_sparse_field.models.fields import Serialized


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
    notification_ids = fields.One2many(
        "shopinvader.notification",
        "backend_id",
        "Notification",
        help="Send mail for predefined events",
    )
    nbr_cart = fields.Integer(compute="_compute_nbr_sale_order")
    nbr_sale = fields.Integer(compute="_compute_nbr_sale_order")
    allowed_country_ids = fields.Many2many(
        comodel_name="res.country", string="Allowed Country"
    )
    anonymous_partner_id = fields.Many2one(
        "res.partner",
        "Anonymous Partner",
        help=("Provide partner settings for unlogged users " "(i.e. fiscal position)"),
        required=True,
        default=lambda self: self.env.ref("shopinvader_v1_base.anonymous"),
    )
    sequence_id = fields.Many2one(
        "ir.sequence", "Sequence", help="Naming policy for orders and carts"
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
    filter_ids = fields.Many2many(comodel_name="product.filter", string="Filter")
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
    website_unique_key = fields.Char(
        required=True,
        copy=False,
        help="This identifier may be provided by each REST request through "
        "a WEBSITE-UNIQUE-KEY http header to identify the target backend. "
        "If not provided by the request and if there is only one backend, "
        "it will be used by default. Otherwise it is possible to override the "
        "_get_backend method into the service context provider component. "
        "The shopinvader_auth_api_key and shopinvader_auth_jwt addons "
        "provides a fallback mechanism in such a case.",
        default=lambda self: self._default_website_unique_key(),
    )
    currency_ids = fields.Many2many(comodel_name="res.currency", string="Currency")

    frontend_data_source = fields.Selection(
        # TODO @simahawk: this value it's here because the form in core module
        # already adds a "search engine" page.
        # I'm not sure it should stay here, it should probalby go to `s_search_engine`.
        selection=[("search_engine", "Search engine")],
        help="Technical field to control form fields appeareance",
        default="search_engine",
    )
    _sql_constraints = [
        (
            "unique_website_unique_key",
            "unique(website_unique_key)",
            _("This website unique key already exists in database"),
        )
    ]

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

    @api.model
    def _default_website_unique_key(self):
        return hashlib.pbkdf2_hmac(
            "sha256", os.urandom(32), os.urandom(32), 100000
        ).hex()

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
            counts = {r["shopinvader_backend_id"][0]: r["__count"] for r in res}
            for rec in self:
                rec[fname] = counts.get(rec.id, 0)

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

    def _get_backend_pricelist(self):
        """The pricelist configure by this backend."""
        # There must be a pricelist somehow: safe fallback to default Odoo one
        return self.pricelist_id or self._default_pricelist_id()

    def _get_customer_default_pricelist(self):
        """Retrieve pricelist to be used for brand new customer record."""
        return self._get_backend_pricelist()

    def _get_partner_pricelist(self, partner):
        """Retrieve pricelist for given res.partner record."""
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

    def _validate_partner(self, shopinvader_partner):
        """Hook to validate partners when required."""
        return True

    @api.model
    @tools.ormcache("self._uid", "website_unique_key")
    def _get_id_from_website_unique_key(self, website_unique_key):
        return self.search([("website_unique_key", "=", website_unique_key)]).id

    @api.model
    def _get_from_website_unique_key(self, website_unique_key):
        return self.browse(self._get_id_from_website_unique_key(website_unique_key))

    def write(self, values):
        if "website_unique_key" in values:
            self._get_id_from_website_unique_key.clear_cache(self.env[self._name])
        with self._keep_binding_sync_with_langs():
            return super(ShopinvaderBackend, self).write(values)
