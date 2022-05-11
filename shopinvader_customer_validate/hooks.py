# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade

from odoo import SUPERUSER_ID, api

OLD_MODULE = "shopinvader_notification_default"
NEW_MODULE = "shopinvader_customer_validate"
RECORD_XMLIDS = [
    # mail.template
    "email_new_customer_welcome_not_validated_notification",
    "email_customer_validated_notification",
    "email_address_created_not_validated_notification",
    "email_address_validated_notification",
    "shopinvader_notification_new_customer_welcome_not_validated",
    "shopinvader_notification_customer_validated",
    "shopinvader_notification_address_created_not_validated",
    "shopinvader_notification_address_validated",
    # ir.ui.view
    "address_created_not_validated",
    "address_validated",
    "new_customer_not_validated",
    "customer_validated",
]


def pre_init_hook(cr):
    update_record_xmlids(cr)


def update_record_xmlids(cr):
    old_module = "shopinvader_notification_default"
    new_module = "shopinvader_customer_validate"
    records_xmlids_spec = [
        (f"{old_module}.{xmlid}", f"{new_module}.{xmlid}") for xmlid in RECORD_XMLIDS
    ]
    openupgrade.rename_xmlids(cr, records_xmlids_spec)
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        openupgrade.set_xml_ids_noupdate_value(env, new_module, RECORD_XMLIDS, True)
