# Copyright 2023 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Shopinvader_v1_product",
    "summary": "Shopinvader Product",
    "version": "14.0.5.24.12",
    "category": "e-commerce",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Akretion",
    "license": "AGPL-3",
    "application": True,
    "installable": True,
    "external_dependencies": {"python": ["cerberus", "unidecode"], "bin": []},
    "depends": [
        "shopinvader_restapi",
        "base_sparse_field",
        "base_rest",
        "jsonifier",
        "base_sparse_field_list_support",
        "base_url",
        "base_vat",
        "component_event",
        "sale",
        "sale_discount_display_amount",
        "server_environment",
        "onchange_helper",
        "queue_job",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/shopinvader_category_security.xml",
        "security/shopinvader_product_security.xml",
        "security/shopinvader_variant_security.xml",
        "wizards/shopinvader_variant_unbinding_wizard.xml",
        "wizards/shopinvader_variant_binding_wizard.xml",
        "wizards/shopinvader_category_binding_wizard.xml",
        "wizards/shopinvader_category_unbinding_wizard.xml",
        "views/shopinvader_menu.xml",
        "views/shopinvader_product_view.xml",
        "views/shopinvader_variant_view.xml",
        "views/shopinvader_category_view.xml",
        "views/shopinvader_backend_view.xml",
        "views/product_view.xml",
        "views/product_filter_view.xml",
        "views/product_category_view.xml",
        "data/ir_export_product.xml",
        "data/ir_export_category.xml",
    ],
    "demo": [
        "demo/product_filter_demo.xml",
        "demo/product_category_demo.xml",
        "demo/product_attribute_value_demo.xml",
        "demo/product_product_demo.xml",
    ],
    "pre_init_hook": "pre_init_hook",
}