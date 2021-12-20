# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Shopinvader Catalog Search Engine Connector",
    "version": "14.0.1.3.3",
    "author": "Akretion",
    "development_status": "Production/Stable",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "license": "AGPL-3",
    "category": "Generic Modules",
    "depends": [
        "shopinvader",
        "connector_search_engine",
        "base_technical_user",
    ],
    "data": [
        "views/shopinvader_backend_view.xml",
        "views/shopinvader_variant_view.xml",
        "views/shopinvader_category_view.xml",
        "data/queue_job_function_data.xml",
    ],
    "installable": True,
    "application": True,
}
