# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def migrate(cr, version):
    """
    For each product and for each template where 'shop_only_quotation' is True,
    set 'shop_order_mode' to 'quotation_only'.
    """
    openupgrade.logged_query(
        cr,
        """
        UPDATE product_template
        SET shop_order_mode = 'quotation_only'
        WHERE shop_only_quotation = 'all_variant';
        """,
    )
    openupgrade.logged_query(
        cr,
        """
        UPDATE product_template
        SET shop_order_mode = 'direct_sale_only'
        WHERE shop_only_quotation = 'never';
        """,
    )
    openupgrade.logged_query(
        cr,
        """
        UPDATE product_template
        SET is_shop_order_mode_enabled_on_variant = TRUE
        WHERE shop_only_quotation = 'manually_on_variant';
        """,
    )

    openupgrade.logged_query(
        cr,
        """
        UPDATE product_product
        SET shop_order_mode = 'quotation_only'
        FROM product_template AS pt
        WHERE product_product.product_tmpl_id = pt.id
        AND pt.is_shop_order_mode_enabled_on_variant = TRUE
        AND product_product.shop_only_quotation = TRUE;
        """,
    )
