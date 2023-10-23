# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader App Demo",
    "summary": """
        Adds a demo application on fastapi endpoint for a
        demo shopinvader application that takes every router
        """,
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "fastapi",
        "shopinvader_api_address",
        "shopinvader_api_cart",
        "shopinvader_api_sale_loyalty",
        "shopinvader_anonymous_partner",
        "shopinvader_fastapi_auth_jwt",
        "shopinvader_product",
        "shopinvader_product_description",
        "shopinvader_product_seo",
        "shopinvader_search_engine",
        "shopinvader_search_engine_image",
        "shopinvader_product_brand",
        "shopinvader_product_brand_tag",
        "shopinvader_search_engine_product_brand_image",
        "connector_elasticsearch",
        "shopinvader_restapi",
        "shopinvader_restapi_auth_jwt",
    ],
    "external_dependencies": {"python": ["fastapi"]},
    "data": [
        "views/fastapi_endpoint.xml",
    ],
    "demo": [
        "demo/res_users.xml",
        "demo/res_groups.xml",
        "demo/auth_jwt_validator.xml",
        "demo/fastapi_endpoint.xml",
        "demo/se_backend.xml",
        "demo/se_index_config.xml",
        "demo/se_index.xml",
        "demo/se_image_field_thumbnail_size.xml",
        "demo/fs_storage.xml",
        "demo/shopinvader_backend.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "shopinvader_v2_app_demo/static/src/js/swagger_ui.js",
        ],
    },
}
