# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Shopinvader Product Stock",
    "summary": "This module is used to choose a stock field during the"
    "export (by backend)",
    "version": "13.0.1.0.0",
    "development_status": "Production/Stable",
    "category": "e-commerce",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Akretion,ACSONE SA/NV,Camptocamp",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "stock",
        "shopinvader",
        "queue_job",
        "connector_search_engine",
        "shopinvader_search_engine",
    ],
    "data": ["views/shopinvader_backend.xml", "data/ir_export_product.xml"],
    "external_dependencies": {"python": ["slugify"]},
}
