# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader API Invoice",
    "summary": "Provides invoice web api via Fastapi",
    "version": "16.0.1.0.1",
    "development_status": "Alpha",
    "category": "Uncategorized",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Camptocamp",
    "license": "AGPL-3",
    "depends": [
        "shopinvader_schema_invoice",
        "shopinvader_api_security_invoice",
        "shopinvader_filtered_model",
        "extendable_fastapi",
        "report_generate_helper",
    ],
    'installable': False,
}
