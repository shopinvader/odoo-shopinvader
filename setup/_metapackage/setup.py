import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-shopinvader-odoo-shopinvader",
    description="Meta package for shopinvader-odoo-shopinvader Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-base_url',
        'odoo14-addon-shopinvader',
        'odoo14-addon-shopinvader_assortment',
        'odoo14-addon-shopinvader_cart_expiry',
        'odoo14-addon-shopinvader_customer_multi_user',
        'odoo14-addon-shopinvader_elasticsearch',
        'odoo14-addon-shopinvader_image',
        'odoo14-addon-shopinvader_invoice',
        'odoo14-addon-shopinvader_locomotive',
        'odoo14-addon-shopinvader_multi_category',
        'odoo14-addon-shopinvader_notification_default',
        'odoo14-addon-shopinvader_product_variant_selector',
        'odoo14-addon-shopinvader_sale_profile',
        'odoo14-addon-shopinvader_search_engine',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
