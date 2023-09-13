{
    "name": "Shopinvader Restapi Helpdesk",
    "summary": "Integrate Helpdesk into Shopinvader Restapi",
    "version": "16.0.1.0.0",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": " Akretion",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "shopinvader_restapi",
        "helpdesk_mgmt",
        "helpdesk_mgmt_sale",  # Sale info on helpdesk tickets
        "base_rest",
        "base_rest_pydantic",
        "extendable",
    ],
    "external_dependencies": {
        "python": [
            "pydantic",
            "pydantic[email]",
            "extendable_pydantic",
        ]
    },
    "data": [
        "security/helpdesk_security.xml",
        "security/ir.model.access.csv",
        "security/ir.model.access.csv",
        "views/helpdesk_settings.xml",
    ],
    "demo": [],
    "qweb": [],
}
