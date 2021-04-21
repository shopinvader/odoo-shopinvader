# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, exceptions, fields, models

from .tools import sanitize_attr_name


class ProductFilter(models.Model):
    _name = "product.filter"
    _description = "Product Filter"
    _order = "sequence,name"

    sequence = fields.Integer()
    based_on = fields.Selection(
        selection=[
            ("field", "Field"),
            ("variant_attribute", "Variant Attribute"),
        ],
        required=True,
    )
    field_id = fields.Many2one(
        "ir.model.fields",
        "Field",
        domain=[
            (
                "model",
                "in",
                ("product.template", "product.product", "shopinvader.product"),
            )
        ],
        ondelete="cascade",
    )
    variant_attribute_id = fields.Many2one(
        string="Attribute",
        comodel_name="product.attribute",
        ondelete="cascade",
    )
    # TODO: rename to not clash w/ built-in
    help = fields.Html(translate=True)
    name = fields.Char(translate=True, required=True)
    # TODO: rename this to `code`, "display_name" makes no sense.
    # Also, in shopinvader_locomotive it is exported as `code`.
    display_name = fields.Char(compute="_compute_display_name")
    # TODO: replace completely `display_name`
    # NOTE: this allows to unify filter/index keys across languages.
    # For prod attributes we'd neeed a unique language agnostic key
    # on product.attribute.
    path = fields.Char(
        help="Enforce external filter key used for indexing and search."
        "Being a path, you can specify a dotted path to an inner value. "
        "Eg: supplier = {id: 1, name: 'Foo'} -> `supplier.name`",
    )

    def _build_display_name(self):
        if self.based_on == "field":
            return self.path or self.field_id.name
        elif self.based_on == "variant_attribute":
            return "variant_attributes.%s" % sanitize_attr_name(
                self.variant_attribute_id
            )

    @api.depends_context("lang")
    def _compute_display_name(self):
        for pfilter in self:
            pfilter.display_name = pfilter._build_display_name()

    @api.constrains("based_on", "field_id", "variant_attribute_id")
    def _contrains_based_on(self):
        based_on_field_error = _(
            "Product filter ID=%d is based on field: requires a field!"
        )
        based_on_attr_error = _(
            "Product filter ID=%d is based on variant attribute: "
            "requires an attribute!"
        )
        for rec in self:
            error = None
            if rec.based_on == "field" and not rec.field_id:
                error = based_on_field_error % rec.id
            elif (
                rec.based_on == "variant_attribute"
                and not rec.variant_attribute_id
            ):
                error = based_on_attr_error % rec.id
            if error:
                raise exceptions.UserError(error)
