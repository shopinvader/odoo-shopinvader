# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Product Seasonality",
    "Summary": """
        Handle product seasonality within shopinvader.
    """,
    "version": "14.0.1.0.1",
    "license": "AGPL-3",
    "author": "Camptocamp SA",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "shopinvader",
        "sale_product_seasonality",
        "component_event",
    ],
    "data": [
        "data/ir_export_product_seasonality.xml",
        "data/queue_job_channel_data.xml",
        "data/queue_job_function_data.xml",
        "security/ir.model.access.csv",
        "views/seasonal_config_line.xml",
        "views/shopinvader_backend.xml",
        "views/shopinvader_seasonal_config.xml",
    ],
    "installable": True,
}
