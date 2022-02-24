# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade

# pylint: disable=odoo-addons-relative-import
from odoo.addons.shopinvader_customer_validate.hooks import (
    NEW_MODULE,
    OLD_MODULE,
    RECORD_XMLIDS,
    update_record_xmlids,
)


def check_installed(cr):
    query = """
        SELECT 1
        FROM ir_model_data
        WHERE module = %(old_module)s
        AND name in %(names)s;
    """
    cr.execute(query, {"old_module": OLD_MODULE, "names": tuple(RECORD_XMLIDS)})
    return cr.fetchone()


def delete_new_records(cr):
    xmlids = [f"{NEW_MODULE}.{xmlid}" for xmlid in RECORD_XMLIDS]
    openupgrade.delete_records_safely_by_xml_id(xmlids)


def migrate(cr, version):
    # The install hook was missing, some mail templates has been created.
    # If shopinvader_notification_default was installed, those records were already there
    # and should have been moved in this module instead.
    # Don't do anything if there's no remaining records for
    # shopinvader_notification_default
    if check_installed(cr):
        # Delete the new mail.templates / ir.ui.views
        delete_new_records(cr)
        # Then we can rename the old records
        update_record_xmlids(cr)
