import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        'depends_override': {
            'base_rest': 'odoo14-addon-base-rest>=14.0.4.0.0',
        },
    }
)
