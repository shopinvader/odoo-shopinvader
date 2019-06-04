# Copyright 2018-2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def _drop_old_index(cr):
    cr.execute(
        "SELECT indexname FROM pg_indexes WHERE indexname = %s",
        ("unique_shopinvader_partner_email",),
    )
    if cr.fetchone():
        cr.execute("DROP INDEX unique_shopinvader_partner_email")


def migrate(cr, version):
    _drop_old_index(cr)
