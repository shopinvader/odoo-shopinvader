# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2019 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Shopinvader Shop Client Connector",
    "version": "12.0.1.0.0",
    "category": "Connector",
    "summary": "Manage communications between Shopinvader and shop client",
    "author": "Akretion, Camptocamp",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "license": "AGPL-3",
    "development_status": "Beta",
    "depends": [
        "connector",
        "connector_search_engine",
        "queue_job",
        "shopinvader",
    ],
    "data": ["views/shopinvader_backend_view.xml", "data/ir_cron.xml"],
    "demo": ["demo/backend_demo.xml"],
    "installable": True,
}
