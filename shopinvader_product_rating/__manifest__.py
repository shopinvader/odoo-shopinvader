# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Shopinvader product rating",
    "summary": """Create user reviews for a product""",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "category": "shopinvader",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "rating",
        "shopinvader",
        "shopinvader_rating_abstract",
        "shopinvader_rating_upvote",
    ],
    "data": [
        "data/ir_export_product.xml",
        "views/rating.xml",
        "views/product_views.xml",
    ],
    "installable": True,
}
