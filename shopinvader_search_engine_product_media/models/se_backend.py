# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError

from odoo.addons.fs_file.fields import FSFile

CDN_HELP_TEXT = """
The URL is one of the fields stored in the media's JSON data exported to the
search engine. The media exported are stored in a filesystem storage.
Therefore, the media is addressable in different ways.
* By default, an internal url can be used to access the media through the
    Odoo server.
* On a fs.storage backend, you can also specify a base url to access the
    media directly through the storage server. This is useful to avoid
    unnecessary load on the Odoo server. This url is available in the
    `url` field of the media's JSON data.
When indexing the media, you can also choose to only export the relative
path of the media. This is useful if you want to use the same storage
backend with different CDN and will reduce the payload size w/o duplicating
data.
To resume, you can choose between 3 options:
* `Odoo URL`: the URL will be the internal URL of the Odoo server
* `FS Storage URL`: the URL will be the URL of the image served by the storage server
* `Relative path URL`: the URL will be the relative path of the image
In the last case, you must take care of adding the CDN URL on your frontend to
all media's relative path.
"""


class SeBackend(models.Model):
    _inherit = "se.backend"

    media_data_url_strategy = fields.Selection(
        selection=[
            ("odoo", "Odoo URL"),
            ("storage_url", "FS Storage URL"),
            ("url_path", "Relative path URL"),
        ],
        help=CDN_HELP_TEXT,
        default="odoo",
    )

    def _get_url_for_media(self, media: FSFile) -> str:
        """Get the URL of the media.
        :param media: The media
        :return: The URL of the media
        """
        self.ensure_one()
        if self.media_data_url_strategy == "odoo":
            value = media.internal_url
        elif self.media_data_url_strategy == "storage_url":
            value = media.url
        elif self.media_data_url_strategy == "url_path":
            value = media.url_path
        else:
            raise ValueError(
                f"Invalid media_data_url_strategy: {self.media_data_url_strategy}"
            )
        if not value:
            raise UserError(
                _(
                    "No URL found for media %(media_name)s with strategy %(strategy)s",
                    media_name=media.name,
                    strategy=self.media_data_url_strategy,
                )
            )
        return value
