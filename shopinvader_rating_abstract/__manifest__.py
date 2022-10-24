# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Shopinvader rating abstract",
    "summary": """Shopinvader abstract service for ratings""",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "category": "shopinvader",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "rating",
        "rating_moderation",
        "shopinvader",
        "shopinvader_search_engine",
    ],
    "data": ["security/shopinvader_security.xml", "data/email_template.xml"],
    "installable": True,
}
