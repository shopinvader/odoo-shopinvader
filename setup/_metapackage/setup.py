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
        'odoo13-addon-shopinvader_search_engine',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
