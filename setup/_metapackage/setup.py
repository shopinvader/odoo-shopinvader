import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-shopinvader-odoo-shopinvader",
    description="Meta package for shopinvader-odoo-shopinvader Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-base_url',
        'odoo12-addon-shopinvader',
        'odoo12-addon-shopinvader_algolia',
        'odoo12-addon-shopinvader_assortment',
        'odoo12-addon-shopinvader_backend_image_proxy',
        'odoo12-addon-shopinvader_cart_expiry',
        'odoo12-addon-shopinvader_category_image_for_product',
        'odoo12-addon-shopinvader_delivery_carrier',
        'odoo12-addon-shopinvader_delivery_instruction',
        'odoo12-addon-shopinvader_demo_app',
        'odoo12-addon-shopinvader_elasticsearch',
        'odoo12-addon-shopinvader_guest_mode',
        'odoo12-addon-shopinvader_image',
        'odoo12-addon-shopinvader_invoice',
        'odoo12-addon-shopinvader_lead',
        'odoo12-addon-shopinvader_locomotive',
        'odoo12-addon-shopinvader_locomotive_algolia',
        'odoo12-addon-shopinvader_locomotive_elasticsearch',
        'odoo12-addon-shopinvader_locomotive_guest_mode',
        'odoo12-addon-shopinvader_multi_category',
        'odoo12-addon-shopinvader_partner_firstname',
        'odoo12-addon-shopinvader_partner_vat',
        'odoo12-addon-shopinvader_pending_cart_reminder',
        'odoo12-addon-shopinvader_product_stock',
        'odoo12-addon-shopinvader_product_stock_state',
        'odoo12-addon-shopinvader_product_variant_selector',
        'odoo12-addon-shopinvader_quotation',
        'odoo12-addon-shopinvader_sale_profile',
        'odoo12-addon-shopinvader_search_engine',
        'odoo12-addon-shopinvader_wishlist',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 12.0',
    ]
)
