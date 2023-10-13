import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-shopinvader-odoo-shopinvader",
    description="Meta package for shopinvader-odoo-shopinvader Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-sale_cart>=16.0dev,<16.1dev',
        'odoo-addon-shopinvader_address>=16.0dev,<16.1dev',
        'odoo-addon-shopinvader_anonymous_partner>=16.0dev,<16.1dev',
        'odoo-addon-shopinvader_api_address>=16.0dev,<16.1dev',
        'odoo-addon-shopinvader_api_cart>=16.0dev,<16.1dev',
        'odoo-addon-shopinvader_fastapi_auth_jwt>=16.0dev,<16.1dev',
        'odoo-addon-shopinvader_product>=16.0dev,<16.1dev',
        'odoo-addon-shopinvader_product_description>=16.0dev,<16.1dev',
        'odoo-addon-shopinvader_product_seo>=16.0dev,<16.1dev',
        'odoo-addon-shopinvader_sale_cart>=16.0dev,<16.1dev',
        'odoo-addon-shopinvader_schema_address>=16.0dev,<16.1dev',
        'odoo-addon-shopinvader_search_engine>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
