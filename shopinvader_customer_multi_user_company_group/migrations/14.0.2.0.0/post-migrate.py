# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    if not version:
        return
    cr.execute(
        """
        UPDATE shopinvader_backend
        SET multi_user_company_group_address_policy =
            multi_user_company_group_records_policy
        """
    )
