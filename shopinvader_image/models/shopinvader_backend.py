# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2022 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

CDN_HELP_TEXT = """
Enable this flag to control
whether the CDN URL must be included or not
in the URL stored in images' JSON data.

OFF: the URL will NOT include the CDN URL (eg: only the relative path);
ON: the URL will include the CDN URL;

Excluding the URL can be useful to:

1. reduce payload size w/o duplicating data
2. allow using the same storage w/ different CDN

If you use this option,
take care of adding the CDN URL on your frontend
to all images' relative path.
"""


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    shopinvader_variant_resize_ids = fields.Many2many(
        comodel_name="shopinvader.image.resize",
        relation="product_image_resize",
        string="Product Image Size",
    )
    shopinvader_category_resize_ids = fields.Many2many(
        comodel_name="shopinvader.image.resize",
        relation="category_image_resize",
        string="Category Image Size",
    )
    # TODO: set default False in v > 15.
    image_data_include_cdn_url = fields.Boolean(
        string="Image URLs w/ CDN",
        help=CDN_HELP_TEXT,
        default=True,
    )
