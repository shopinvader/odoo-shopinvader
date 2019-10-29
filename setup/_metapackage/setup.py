import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-shopinvader-odoo-shopinvader",
    description="Meta package for shopinvader-odoo-shopinvader Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-shopinvader_locomotive_elasticsearch',
        'odoo12-addon-shopinvader_pending_cart_reminder',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
