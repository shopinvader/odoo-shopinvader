# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    company = fields.Char("Company", index=True)
    contact_name = fields.Char(
        "Contact name",
        index=True,
        # We don't have to copy it to avoid issue
        copy=False,
    )

    name = fields.Char(
        compute="_compute_name", required=False, store=True, readonly=True
    )

    @api.multi
    def copy(self, default=None):
        """Ensure partners are copied right.

        Odoo adds ``(copy)`` to the end of :attr:`~.name`, but that would get
        ignored in :meth:`~.create` because it also copies explicitly firstname
        and lastname fields.
        """
        return super(ResPartner, self.with_context(copy=True)).copy(default)

    @api.multi
    @api.depends("company", "contact_name")
    def _compute_name(self):
        """Write the 'name' field according to splitted data."""
        for record in self:
            name = u", ".join(
                [p for p in (record.company, record.contact_name) if p]
            )
            record.name = name

    @api.multi
    def _inverse_name(self):
        """Try to revert the effect of :meth:`._compute_name`."""
        for record in self:
            names = record.name.split(", ", 1)
            if record.is_company:
                company = names[0]
                contact_name = len(names) > 1 and names[1] or ""
            else:
                company = len(names) > 1 and names[0] or ""
                contact_name = len(names) > 1 and names[1] or names[0]
            record.company = company
            record.contact_name = contact_name

    @api.multi
    def name_get(self):
        res = []
        for partner in self:
            name = partner.name or ""

            if partner.company_name or partner.parent_id:
                if not name and partner.type in [
                    "invoice",
                    "delivery",
                    "other",
                ]:
                    name = dict(
                        self.fields_get(["type"])["type"]["selection"]
                    )[partner.type]
            if self._context.get("show_address_only"):
                name = partner._display_address(without_company=True)
            if self._context.get("show_address"):
                name = (
                    name
                    + "\n"
                    + partner._display_address(without_company=True)
                )
            name = name.replace("\n\n", "\n")
            name = name.replace("\n\n", "\n")
            if self._context.get("show_email") and partner.email:
                name = "{} <{}>".format(name, partner.email)
            if self._context.get("html_format"):
                name = name.replace("\n", "<br/>")
            res.append((partner.id, name))
        return res

    @api.depends(
        "is_company", "name", "type", "company_name", "company", "contact_name"
    )
    def _compute_display_name(self):
        diff = dict(show_address=None, show_address_only=None, show_email=None)
        names = dict(self.with_context(**diff).name_get())
        for partner in self:
            partner.display_name = names.get(partner.id)

    def _process_name(self, vals):
        # The aim is only to solve issue with compatibility with existing
        # module and to resolve testing issue
        updated_vals = vals.copy()
        if "contact_name" in updated_vals:
            raise UserError(
                _(
                    "You can not pass the contact_name and the name at the "
                    "same time"
                )
            )
        updated_vals["contact_name"] = updated_vals["name"]
        del updated_vals["name"]
        _logger.debug(
            "Be carefull the field name have been rename to contact_name"
        )
        return updated_vals

    @api.model
    def create(self, vals):
        if "name" in vals:
            vals = self._process_name(vals)
        # As name is required but it's a computed field
        # we need to set a fake value that will be recomputed
        vals["name"] = "/"
        return super(ResPartner, self).create(vals)

    @api.multi
    def write(self, vals):
        if "name" in vals:
            self._process_name(vals)
        return super(ResPartner, self).write(vals)
