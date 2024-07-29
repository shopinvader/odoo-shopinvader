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

ALT_HELP_TEXT = """
The alt name of an image is used to provide a meaningful description.
The alt name can be configured by image, but it can also be empty.
When it's empty, the product name will be used as a fallback.
When this flag is enabled, the alt name will be empty.
You can then choose on your shop how to populate it.
This helps reducing the amount of data stored in the database
when the alt name is always equal to the product name.
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
    image_data_empty_alt_name_allowed = fields.Boolean(
        string="Image ALT name can be empty",
        help=ALT_HELP_TEXT,
        default=False,
    )
