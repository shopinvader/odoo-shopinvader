# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    """existing urls should not be synced."""

    cr.execute(
        """
           update shopinvader_product
           set automatic_url_key = url_key
       """
    )
