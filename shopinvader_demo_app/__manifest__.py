# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Shopinvader Demo App",
    "version": "12.0.2.0.5",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "license": "AGPL-3",
    "category": "Generic Modules",
    "depends": [
        "shopinvader",
        "shopinvader_assortment",
        "shopinvader_guest_mode",
        "shopinvader_locomotive",
        "shopinvader_locomotive_guest_mode",
        "shopinvader_locomotive_elasticsearch",
        "shopinvader_delivery_carrier",
        "shopinvader_product_stock",
        "shopinvader_image",
        "shopinvader_elasticsearch",
        "shopinvader_payment_manual",
        "shopinvader_payment_stripe",
        "product_brand",
    ],
    "data": ["data/ir_export_product.xml"],
    "demo": [
        "demo/product_brand_demo.xml",
        "demo/product_product_demo.xml",
        "demo/se_backend_elasticsearch_demo.xml",
        "demo/storage_backend_demo.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": True,
}
