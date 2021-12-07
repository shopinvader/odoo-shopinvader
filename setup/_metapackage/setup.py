import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-shopinvader-odoo-shopinvader",
    description="Meta package for shopinvader-odoo-shopinvader Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-base_url',
        'odoo8-addon-connector_generic',
        'odoo8-addon-connector_locomotivecms',
        'odoo8-addon-partner_contact_company',
        'odoo8-addon-product_media',
        'odoo8-addon-product_online_category',
        'odoo8-addon-product_rating',
        'odoo8-addon-product_stock_state',
        'odoo8-addon-product_tag',
        'odoo8-addon-shopinvader',
        'odoo8-addon-shopinvader_algolia',
        'odoo8-addon-shopinvader_claim',
        'odoo8-addon-shopinvader_google_shopping',
        'odoo8-addon-shopinvader_lead',
        'odoo8-addon-shopinvader_m2mcategories',
        'odoo8-addon-shopinvader_mailjet',
        'odoo8-addon-shopinvader_paypal',
        'odoo8-addon-shopinvader_price_per_qty',
        'odoo8-addon-shopinvader_product_link',
        'odoo8-addon-shopinvader_product_media',
        'odoo8-addon-shopinvader_product_rating',
        'odoo8-addon-shopinvader_product_tag',
        'odoo8-addon-shopinvader_promotion_rule',
        'odoo8-addon-shopinvader_reset_password',
        'odoo8-addon-shopinvader_search_engine',
        'odoo8-addon-shopinvader_stripe',
        'odoo8-addon-shopinvader_visible_discount',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 8.0',
    ]
)
