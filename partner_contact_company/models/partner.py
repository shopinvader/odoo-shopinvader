# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    company = fields.Char()

    def _sync_company_name(self):
        for record in self:
            if record.is_company:
                for contact in record.child_ids:
                    if contact.use_parent_address:
                        contact.company = record.name
            elif record.parent_id and record.use_parent_address:
                for contact in record.child_ids:
                    contact.company = record.company

    @api.multi
    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        self._sync_company_name()
        return res

    @api.model
    def create(self, vals):
        partner = super(ResPartner, self).create(vals)
        partner._sync_company_name()
        return partner

    @api.onchange('parent_id', 'use_parent_address', 'is_company')
    def onchange_company(self):
        if self.is_company:
            self.company = None
        elif self.parent_id.is_company:
            self.company = self.parent_id.name

    @api.multi
    def name_get(self):
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
                name = name.replace('\n\n','\n')
                name = name.replace('\n\n','\n')
            res.append((record.id, name))
        return res
