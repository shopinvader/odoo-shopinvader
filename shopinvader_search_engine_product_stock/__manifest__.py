# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Shopinvader Search Engine Product Stock",
    "summary": "This module is used to export stock data to search engine",
    "version": "16.0.1.0.3",
    "development_status": "Alpha",
    "category": "e-commerce",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Akretion,ACSONE SA/NV,Camptocamp",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["stock", "shopinvader_search_engine"],
    "data": [
        "views/se_backend.xml",
        "views/se_index.xml",
        "data/queue_job_channel_data.xml",
        "data/queue_job_function_data.xml",
    ],
    "external_dependencies": {"python": ["slugify"]},
}
