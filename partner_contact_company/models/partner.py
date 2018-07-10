# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    """Inhance the feature of Partner."""

    _inherit = 'res.partner'

    company = fields.Char()

    def _sync_company_name(self):
        """The methos used to set company name."""
        for record in self:
            if record.is_company:
                for contact in record.child_ids:
                    contact.company = record.name
            elif record.parent_id:
                for contact in record.child_ids:
                    contact.company = record.company

    @api.multi
    def write(self, vals):
        """Override the method to set company name."""
        res = super(ResPartner, self).write(vals)
        self._sync_company_name()
        return res

    @api.model
    def create(self, vals):
        """Override the method to add company name."""
        partner = super(ResPartner, self).create(vals)
        partner._sync_company_name()
        return partner

    @api.onchange('parent_id', 'is_company')
    def onchange_company(self):
        """The method used to set company name to it's child."""
        if self.is_company:
            self.company = None
        elif self.parent_id.is_company:
            self.company = self.parent_id.name

    @api.multi
    def name_get(self):
        """Override the method set name of partner."""
        res = []
        for record in self:
            record_id, name = super(ResPartner, record).name_get()[0]
            ctx = self._context
            if not ctx.get('show_address_only'):
                if record.company:
                    name = "%s, %s" % (record.company, record.name)
                else:
                    name = record.name
                if ctx.get('show_email') and record.email:
                    name = "%s <%s>" % (name, record.email)
                if ctx.get('show_address'):
                    name = name + "\n" + self._display_address(
                        record, without_company=True)
                if name:
                    name = name.replace('\n\n', '\n')
            res.append((record.id, name))
        return res
