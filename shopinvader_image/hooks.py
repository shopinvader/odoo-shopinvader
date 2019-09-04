# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (http://acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, tools
from odoo.api import Environment
from odoo.modules.module import get_resource_path

DEMO_POST_INIT = [
    "demo/storage_file_demo.xml",
    "demo/storage_image_demo.xml",
    "demo/product_image_relation_demo.xml",
    "demo/product_product_image_relation_demo.xml",
]


def load_xml(env, module, filepath):
    tools.convert_file(
        env.cr,
        module,
        get_resource_path(module, filepath),
        {},
        mode="init",
        noupdate=False,
    )


def post_init_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    module_obj = env["ir.module.module"]
    module = module_obj.search([("name", "=", "shopinvader_image")])
    if module.demo:
        #  loaded data requires that the component registry is loaded
        builder = env["component.builder"]
        # build the components of every installed addons
        comp_registry = builder._init_global_registry()
        builder.build_registry(comp_registry, states=("installed",))
        # build the components of the current tested addon
        env["component.builder"].load_components("shopinvader_image")
        # load data requiring components
        for demo in DEMO_POST_INIT:
            load_xml(env, "shopinvader_image", demo)
        # prevent removal of demo data since the xml files are not declared
        # into the demo section and therefore the xml_ids are no more found on
        # addon update
        cr.execute(
            """
            update
                ir_model_data
            set
                module='__export__'
            where
                module='shopinvader_image'
                and model in (
                    'storage.file',
                    'storage.image',
                    'product.image.relation',
                    'product.product'
                )
        """
        )
