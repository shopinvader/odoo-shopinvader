# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    locomotivecms_bind_ids = fields.One2many(
        'locomotivecms.product',
        'record_id',
        string='Locomotive Binding')


class LocomotivecmsProduct(models.Model):
    _name = 'locomotivecms.product'
    _inherit = 'locomotivecms.binding'
    _inherits = {'product.template': 'record_id'}

    record_id = fields.Many2one(
        'product.template',
        required=True,
        ondelete='cascade')

    _sql_constraints = [
        ('record_uniq', 'unique(backend_id, record_id)',
        'A product can only have one binding by backend.'),
    ]

    #Automatically create the locomotive binding for the image
    @api.model
    def create(self, vals):
        binding = super(LocomotivecmsProduct, self).create(vals)
        binding_image_obj = \
            self.env['locomotivecms.image'].with_context(
                connector_no_export=True)
        for image in binding.image_ids:
            for size in binding_image_obj._image_size:
                binding_image_obj.create({
                    'size': size,
                    'record_id': image.id,
                    'backend_id': binding.backend_id.id,
                    })
        return binding


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    def _pricelist_key(self):
        "You can customise this method if you want a "
        "more explicit key in the pricelist json"
        self.ensure_one()
        return str(self.id)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # TODO adding a field is maybe not the best solution
    # indeed if we need to customise the export per backend
    # it's not possible. We need to refcator the base module
    # to have more compatibility between json export and mapping
    # the big question to solve is does the mapping system using exporter
    # is the good solution
    pricelist = fields.Serialized(compute='_compute_price')

    def _get_rounded_price(self, pricelist, qty):
        self.ensure_one()
        price = pricelist.price_get(self.id, qty, None)[pricelist.id]
        return pricelist.currency_id.round(price)

    def _get_dict_price(self, pricelist):
        # we add an extra key here "values" to give the posibility to add
        # some extra information easily (with new keys) without changing
        # the data format and so simplifying the template compatibility
        res = {'values': []}
        items = self.env['product.pricelist.item'].search([
            ('price_version_id.pricelist_id', '=', pricelist.id)
            ])
        item_qty = set([item.min_quantity
                        for item in items if item.min_quantity > 1] + [1])
        for qty in item_qty:
            res['values'].append(
                {'qty': qty, 'price': self._get_rounded_price(pricelist, qty)})
        return {pricelist._pricelist_key(): res}

    def _compute_price(self):
        for record in self:
            pls = self.env['product.pricelist'].search([('type', '=', 'sale')])
            res = {}
            for pl in pls:
                res.update(record._get_dict_price(pl))
            record.pricelist = res
