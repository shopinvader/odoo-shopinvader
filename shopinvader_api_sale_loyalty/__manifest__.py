# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader API Sale Loyalty",
    "summary": """
        FastAPI services to add coupons and loyalties to carts.""",
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "sale_loyalty",
        "sale_loyalty_order_info",
        "shopinvader_api_cart",
        "shopinvader_api_security_sale",
        "shopinvader_schema_sale",
        "pydantic",
        "extendable",
        "fastapi",
        "extendable_fastapi",
    ],
    "data": [
        "security/groups.xml",
        "security/acl_loyalty_card.xml",
        "security/acl_loyalty_program.xml",
        "security/acl_loyalty_reward.xml",
        "security/acl_loyalty_rule.xml",
        "security/acl_product_product.xml",
        "security/acl_product_tag.xml",
        "security/acl_sale_order_coupon_points.xml",
        "security/acl_sale_loyalty_reward_wizard.xml",
    ],
    "external_dependencies": {
        "python": [
            "fastapi",
            "pydantic>=2.0.0",
            "extendable-pydantic>=1.2.0",
        ]
    },
}
