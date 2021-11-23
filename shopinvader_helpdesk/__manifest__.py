{
    "name": "Invader Helpdesk",
    "summary": "Integrate Helpdesk into Shopinvader",
    "version": "14.0.1.0.0",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": " Akretion",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "shopinvader",
        "helpdesk_mgmt_rest_api",  # OCA version
        "helpdesk_mgmt_sale",  # Sale info on helpdesk tickets
    ],
    "data": [
        "security/ir.model.access.csv",
    ],
    "demo": [],
    "qweb": [],
}
