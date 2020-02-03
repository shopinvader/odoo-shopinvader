# Copyright 2018 Akretion (http://www.akretion.com).
# Author: Sylvain Calador (<https://www.akretion.com>)
# Author: Saritha Sahadevan (<https://www.cybrosys.com>)
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Import Shopinvader product image",
    "version": "13.0.1.0.0",
    "summary": "Import product images",
    "author": "Akretion, Camptocamp",
    "company": "Akretion",
    "maintainer": "Akretion",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "category": "Product",
    "depends": ["shopinvader_image"],
    "external_dependencies": {"python": ["magic", "validators"]},
    "data": ["wizards/import_product_image_view.xml"],
    "license": "AGPL-3",
    "installable": True,
}
