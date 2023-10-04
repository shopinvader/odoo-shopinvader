# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2022 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError

from odoo.addons.fs_image.fields import FSImageValue

CDN_HELP_TEXT = """

The URL is one of the fields stored in the image's JSON data exported to the
search engine. The images exported are stored in a filesystem storage.
Therefore, the image is addressable in a different.

* By default, an internal url can be used to access the image through the
    Odoo server.
* On a fs.storage backend, you can also specifiy a base url to access the
    image directly through the storage server. This is useful to avoid
    unnecessary load on the Odoo server. This url is available in the
    `url`field of the image's JSON data.

When indexing the images, you can also choose to only export the relative
path of the image. This is useful if you want to use the same storage
backend with different CDN and will reduce the payload size w/o duplicating
data.

To resume, you can choose between 3 options:

* `Odoo URL`: the URL will be the internal URL of the Odoo server
* `FS Storage URL`: the URL will be the URL of the image served by the storage server
* `Relative path URL`: the URL will be the relative path of the image

In the last case, you must take care of adding the CDN URL on your frontend to
all images' relative path.
"""


class SeBackend(models.Model):
    _inherit = "se.backend"

    image_data_url_strategy = fields.Selection(
        selection=[
            ("odoo", "Odoo URL"),
            ("storage_url", "FS Storage URL"),
            ("url_path", "Relative path URL"),
        ],
        help=CDN_HELP_TEXT,
        default="odoo",
    )

    def _get_image_url_for_image(self, image: FSImageValue) -> str:
        """Get the URL of the image.

        :param image: The image
        :return: The URL of the image
        """
        self.ensure_one()
        if self.image_data_url_strategy == "odoo":
            value = image.internal_url
        elif self.image_data_url_strategy == "storage_url":
            value = image.url
        elif self.image_data_url_strategy == "url_path":
            value = image.url_path
        else:
            raise ValueError(
                f"Invalid image_data_url_strategy: {self.image_data_url_strategy}"
            )
        if not value:
            raise UserError(
                _(
                    "No URL found for image %(image_name)s with strategy %(strategy)s",
                    image_name=image.name,
                    strategy=self.image_data_url_strategy,
                )
            )
        return value
