import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-shopinvader-odoo-shopinvader",
    description="Meta package for shopinvader-odoo-shopinvader Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-base_url',
        'odoo13-addon-shopinvader',
        'odoo13-addon-shopinvader_algolia',
        'odoo13-addon-shopinvader_assortment',
        'odoo13-addon-shopinvader_cart_expiry',
        'odoo13-addon-shopinvader_customer_multi_user',
        'odoo13-addon-shopinvader_delivery_carrier',
        'odoo13-addon-shopinvader_elasticsearch',
        'odoo13-addon-shopinvader_image',
        'odoo13-addon-shopinvader_import_image',
        'odoo13-addon-shopinvader_locomotive',
        'odoo13-addon-shopinvader_locomotive_algolia',
        'odoo13-addon-shopinvader_partner_firstname',
        'odoo13-addon-shopinvader_product_variant_selector',
        'odoo13-addon-shopinvader_search_engine',
        'odoo13-addon-shopinvader_wishlist',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
