# Copyright 2021 KMEE (http://www.kmee.com.br).
# @author Daniel Sadamo <daniel.sadamo@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Brazilian Localization Shopinvader",
    "summary": "Shopinvader localization"
    "Adds fields from brazilian legislation to shopinvader e-commerce",
    "version": "14.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": " KMEE INFORMATICA LTDA",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [
            "erpbrasil.base>=2.3.0",
        ],
        "bin": [],
    },
    "depends": [
        "l10n_br_zip",
        "shopinvader_base_address_city",
        "shopinvader_base_address_extended",
        "shopinvader_delivery_carrier",
    ],
    "data": ["views/delivery_view.xml"],
}
