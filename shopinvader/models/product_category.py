# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv import expression


class ProductCategory(models.Model):
    _inherit = "product.category"

    shopinvader_bind_ids = fields.One2many(
        "shopinvader.category",
        "record_id",
        string="Shopinvader Binding",
        context={"active_test": False},
    )
    filter_ids = fields.Many2many(
        comodel_name="product.filter", string="Filter"
    )
    active = fields.Boolean(default=True, inverse="_inverse_active")

    def _inverse_active(self):
        categories = self.filtered(lambda p: not p.active)
        categories = categories.with_prefetch(self._prefetch_ids)
        categories.mapped("shopinvader_bind_ids").write({"active": False})

    # V13 restore translate on category name...
    # This code is a transversal fix and should go into a dedicated addon...
    # The translate=True has been removed in
    # https://github.com/odoo/odoo/pull/36717 to workaround a bug introduced
    # in https://github.com/odoo/odoo/pull/16220 To avoid a bug into the seach
    # on category name, we must also restore the name_get method and
    # name_search
    # see also https://github.com/odoo/odoo/issues/22060#issuecomment-356567683
    _rec_name = None
    name = fields.Char(translate=True)

    def name_get(self):
        def get_names(cat):
            """ Return the list [cat.name, cat.parent_id.name, ...] """
            res = []
            while cat and cat.id:
                res.append(cat.name)
                cat = cat.parent_id
            return res

        return [(cat.id, " / ".join(reversed(get_names(cat)))) for cat in self]

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        if not args:
            args = []
        if name:
            # Be sure name_search is symetric to name_get
            category_names = name.split(" / ")
            parents = list(category_names)
            child = parents.pop()
            domain = [("name", operator, child)]
            if parents:
                names_ids = self.name_search(
                    " / ".join(parents),
                    args=args,
                    operator="ilike",
                    limit=limit,
                )
                category_ids = [name_id[0] for name_id in names_ids]
                if operator in expression.NEGATIVE_TERM_OPERATORS:
                    categories = self.search([("id", "not in", category_ids)])
                    domain = expression.OR(
                        [[("parent_id", "in", categories.ids)], domain]
                    )
                else:
                    domain = expression.AND(
                        [[("parent_id", "in", category_ids)], domain]
                    )
                for i in range(1, len(category_names)):
                    domain = [
                        # fmt: off
                        [
                            (
                                "name",
                                operator,
                                " / ".join(category_names[-1 - i:]),
                            )
                        ],
                        # fmt: on
                        domain
                    ]
                    if operator in expression.NEGATIVE_TERM_OPERATORS:
                        domain = expression.AND(domain)
                    else:
                        domain = expression.OR(domain)
            categories = self.search(
                expression.AND([domain, args]), limit=limit
            )
        else:
            categories = self.search(args, limit=limit)
        return categories.name_get()
