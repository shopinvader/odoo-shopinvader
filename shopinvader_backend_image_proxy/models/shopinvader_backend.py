# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from urllib.parse import ParseResult, urljoin, urlparse

from odoo import fields, models


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    image_proxy_url = fields.Char(
        help="Replace the original url (base part) by this proxy url during "
        "export of images serialized field.\n"
        "Fill without specifying the protocol or anything else than the "
        "complete website name (with subdomain if any).\n"
        "Example: my.website.com"
    )

    def _replace_by_proxy(self, url):
        """
        This function is used to replace the website (into url parameter)
        by the one set on the current recordset (image_proxy_url field).
        Example:
        url = "http://subdomain.example.com/abc/shopinvader.png?a=awesome"
        self.image_proxy_url = "https://anonymous.shopinvader.com/test"
        Expected result:
        "https://anonymous.shopinvader.com/test/shopinvader.png?a=myself"
        So we have to replace the protocol (http, https,...) and keep only
        the final part (file name with arguments)
        :param url: str
        :return: str
        """
        self.ensure_one()
        proxy_url = self.image_proxy_url
        if proxy_url and url:
            if not proxy_url.endswith("/"):
                proxy_url = proxy_url + "/"
            parts = urlparse(url)
            path = parts.path.split("/")[-1]
            path = ParseResult("", "", path, *parts[3:]).geturl()
            return urljoin(proxy_url, path)
        return url
