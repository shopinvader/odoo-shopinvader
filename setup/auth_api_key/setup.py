import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        'depends_override': {
            'keychain': 'odoo10_addon_keychain>=10.0.1.0.0.99.dev11',
        },
    }
)
