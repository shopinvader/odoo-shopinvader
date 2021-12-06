# Copyright 2021 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Product Stock Forecast Expiry",
    "summary": "Integrates product lot expiration into the forecast",
    "version": "14.0.1.0.0",
    "author": "Camptocamp SA",
    "maintainers": ["ivantodorovich"],
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "license": "AGPL-3",
    "category": "Shopinvader",
    "depends": ["shopinvader_product_stock_forecast", "product_expiry"],
    "data": ["views/shopinvader_backend.xml"],
}
