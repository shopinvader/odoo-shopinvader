# Copyright 2021 Camptocamp (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Easy Binding",
    "summary": "Easily manage Shopinvader bindings for your company backend.",
    "version": "14.0.1.0.1",
    "author": "Camptocamp SA",
    "maintainers": ["ivantodorovich"],
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "license": "AGPL-3",
    "category": "Shopinvader",
    "depends": ["shopinvader"],
    "data": [
        "views/res_config_settings.xml",
        "views/product_template.xml",
    ],
    "demo": [
        "demo/res_company.xml",
    ],
    "post_init_hook": "post_init_hook",
}
