# Copyright 2021 Camptocamp (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tools.sql import column_exists, create_column


def migrate(cr, version):
    """Migrate only_quotation field

    - Copy product.template values to product.product
    - Rename to shop_only_quotation
    """
    if (
        not version
        or column_exists(cr, "product_product", "shop_only_quotation")
        or not column_exists(cr, "product_template", "only_quotation")
    ):
        return
    create_column(cr, "product_product", "shop_only_quotation", "BOOLEAN")
    cr.execute(
        """
            UPDATE product_product pp
            SET shop_only_quotation = pt.only_quotation
            FROM product_template pt
            WHERE pp.product_tmpl_id = pt.id
        """
    )
    cr.execute("ALTER TABLE product_template DROP COLUMN only_quotation")
