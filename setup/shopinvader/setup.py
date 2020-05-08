import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        "external_dependencies_override": {
            "python": {
                "cerberus": "Cerberus>=1.3.2",
            },
        },
    }
)
