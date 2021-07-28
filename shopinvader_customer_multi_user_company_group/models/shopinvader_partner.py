# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv import expression


class ShopinvaderPartner(models.Model):
    _inherit = "shopinvader.partner"

    is_company_group_user = fields.Boolean(
        compute="_compute_is_company_group_user",
        help="If true, means the partner belongs to the main company group",
    )

    @api.depends("company_group_id", "main_partner_id")
    def _compute_is_company_group_user(self):
        for rec in self:
            rec.is_company_group_user = (
                rec.main_partner_id == rec.company_group_id or not rec.company_group_id
            )

    def _make_partner_domain(self, partner_field, operator="="):
        res = super()._make_partner_domain(partner_field, operator=operator)
        if not self.is_company_group_user:
            return res
        # The hierarchy when dealing with company_groups is trickier as company_group
        # is not really a part of the parent_id / child_ids hierarchy.
        # More often than not, the company group partner won't have a company_group_id
        # set itself. One would expect a circular reference to itself there, so:
        company_group = self.company_group_id or self.commercial_partner_id
        domain_field = (
            f"{partner_field}.company_group_id"
            if partner_field != "id"
            else "company_group_id"
        )
        # Main users can always see everything down their hierarchy and companies
        # belonging to the group hierarchy.
        if self.is_admin_account or self.is_main_account:
            return expression.OR(
                [
                    res,
                    [(domain_field, "child_of", company_group.id)],
                ]
            )
        # If we are logged as or in the company group itself, we can see all the
        # public records down our group member's hierarchies.
        return expression.OR(
            [
                res,
                [(domain_field, operator, company_group.id)],
            ]
        )

    def _make_address_domain(self):
        res = super()._make_address_domain()
        if not self.is_company_group_user:
            return res
        # The hierarchy when dealing with company_groups is trickier as company_group
        # is not really a part of the parent_id / child_ids hierarchy.
        # More often than not, the company group partner won't have a company_group_id
        # set itself. One would expect a circular reference to itself there, so:
        company_group = self.company_group_id or self.commercial_partner_id
        # Main users can always see everything down their hierarchy and companies
        # belonging to the group hierarchy.
        if self.is_admin_account or self.is_main_account:
            return expression.OR(
                [res, [("company_group_id", "child_of", company_group.id)]]
            )
        # If we are logged as or in the company group itself, we can see all the
        # public records down our group member's hierarchies.
        return expression.OR(
            [
                res,
                [
                    ("company_group_id", "child_of", company_group.id),
                    ("shopinvader_bind_ids", "=", False),
                    ("invader_address_share_policy", "=", "public"),
                ],
            ]
        )
