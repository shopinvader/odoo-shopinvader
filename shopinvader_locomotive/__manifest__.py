# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Shopinvader Locomotive CMS Connector",
    "version": "14.0.1.1.0",
    "category": "Connector",
    "summary": "Manage communications between Shopinvader and Locomotive CMS",
    "author": "Akretion",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "license": "AGPL-3",
    "development_status": "Production/Stable",
    "depends": [
        "connector",
        "shopinvader_search_engine",
        "queue_job",
        "shopinvader",
    ],
    "data": [
        "views/shopinvader_backend_view.xml",
        "views/product_filter_view.xml",
        "data/ir_cron.xml",
        "data/queue_job_function_data.xml",
    ],
    "demo": ["demo/backend_demo.xml"],
    "external_dependencies": {"python": ["locomotivecms"]},
    "installable": True,
    "auto_install": False,
    "application": False,
}
