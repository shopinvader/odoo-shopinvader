# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com)
# Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def post_init_hook(cr, registry):
    module_obj = registry['ir.module.module']
    product_obj = registry['product.template']
    data_obj = registry['ir.model.data']
    module_ids = module_obj.search(
        cr, 1, [('name', '=', 'shopinvader_algolia')])
    module = module_obj.browse(cr, 1, module_ids[0])
    if module.demo:
        product_id = data_obj.xmlid_to_res_id(
            cr, 1, 'product.product_product_4_product_template')
        description = product_obj.browse(cr, 1, product_id).description
        vals = {'description': description}
        product_ids = product_obj.search(cr, 1, [])
        product_obj.write(cr, 1, product_ids, vals)
