# Copyright 2022 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# @author Matthieu Méquignon <matthieu.mequignon@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Shopinvader Data Stored",
    "version": "14.0.1.0.0",
    "author": "Camptocamp",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "license": "AGPL-3",
    "category": "Shopinvader",
    "depends": [
        "shopinvader",
        "jsonify_stored",
    ],
    "data": [
        "views/shopinvader_variant_view.xml",
    ],
    "pre_init_hook": "pre_init_hook",
    "installable": True,
}
