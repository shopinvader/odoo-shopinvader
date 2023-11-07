{
    "name": "Shopinvader Api Quotation",
    "summary": "Shopinvader Quotation",
    "version": "16.0.1.0.1",
    "category": "e-commerce",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Akretion",
    "license": "AGPL-3",
    "depends": ["crm", "fastapi", "shopinvader_schema_sale", "shopinvader_api_cart"],
    "external_dependencies": {
        "python": [
            "fastapi",
            "pydantic>=2.0.0",
            "extendable_pydantic>=1.0.0",
        ]
    },
    "installable": True,
}
