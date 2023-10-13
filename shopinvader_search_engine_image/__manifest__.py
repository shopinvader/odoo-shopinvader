# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2023 ACSONE SA/NV (<http://acsone.eu>)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Shopinvader image",
    "summary": "Add the export of Image for Shopinvader",
    "version": "16.0.1.0.0",
    "category": "e-commerce",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Akretion, ACSONE SA/NV",
    "license": "AGPL-3",
    "depends": [
        "shopinvader_search_engine",
        "search_engine_image_thumbnail",
        "fs_product_multi_image",
    ],
    "data": [
        "views/se_backend.xml",
    ],
    "demo": [
        "demo/image_tag.xml",
        "demo/se_thumbnail_size.xml",
        "demo/fs_product_image.xml",
    ],
    "installable": True,
    "development_status": "Alpha",
}
