# Copyright 2017 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Shopinvader Carrier",
    "summary": "Carrier integration for Shopinvader",
    "version": "16.0.1.0.0",
    "category": "e-commerce",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Akretion, Acsone",
    "license": "AGPL-3",
    "application": True,
    "installable": True,
    "external_dependencies": {
        "python": [
            "fastapi",
            "pydantic>=2.0.0",
            "extendable-pydantic>=1.2.0",
        ],
    },
    "depends": [
        "delivery",
        # OCA/delivery-carrier
        "delivery_carrier_info",
        # OCA/queue
        "queue_job",
        # OCA/sale-workflow
        "sale_shipping_info_helper",
        "sale_discount_display_amount",
        # Shopinvader
        "pydantic",
        "extendable",
        "fastapi",
        "extendable_fastapi",
        "shopinvader_api_cart",
        "shopinvader_api_security_sale",
        "shopinvader_delivery_carrier",
        "shopinvader_filtered_model",
        "shopinvader_sale_cart",
        "shopinvader_schema_sale",
    ],
    "data": [
        "security/groups.xml",
        "security/acl_delivery_carrier.xml",
        "security/acl_choose_delivery_carrier.xml",
        "security/acl_product_pricelist_item.xml",
        "security/acl_product_pricelist.xml",
        "security/acl_product_category.xml",
        "security/acl_account_tax.xml",
        "security/acl_sale_order.xml",
        "security/acl_sale_order_line.xml",
        "security/acl_product_template.xml",
        "security/acl_product_product.xml",
        "security/acl_stock_picking.xml",
        "security/acl_stock_picking_type.xml",
    ],
}
