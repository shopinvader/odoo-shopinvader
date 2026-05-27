# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Api Mass Mailing",
    "version": "16.0.1.0.0",
    "author": "Akretion, Odoo Community Association (OCA)",
    "summary": "Add a way to subscribe/unsubscribe to mass mailing list of an endpoint",
    "category": "Marketing",
    "depends": [
        "mass_mailing",
        "extendable_fastapi",
    ],
    "external_dependencies": {
        "python": [
            "fastapi",
            "pydantic>=2.0.0",
            "extendable-pydantic>=1.2.0",
        ]
    },
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "data": [
        "security/res_groups.xml",
        "security/acl_mass_mailing.xml",
        "views/fastapi_endpoint_views.xml",
    ],
    "maintainers": ["paradoxxxzero"],
    "installable": True,
    "license": "AGPL-3",
}
