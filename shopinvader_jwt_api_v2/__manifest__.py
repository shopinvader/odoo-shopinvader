# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Api V2 for JWT",
    "description": """
        Add entry point for shopinvader api V2""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "shopinvader_auth_jwt",
        "shopinvader_sale_cart",
        "shopinvader_sale_cart_delivery",
    ],
    "data": ["views/shopinvader_menu.xml"],
    "demo": [],
}
