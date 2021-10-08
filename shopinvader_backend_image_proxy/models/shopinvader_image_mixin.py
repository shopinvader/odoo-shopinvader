# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class ShopinvaderImageMixin(models.AbstractModel):
    _inherit = "shopinvader.image.mixin"

    def _prepare_data_resize(self, thumbnail, image_relation):
        """
        Prepare data to fill images serialized field
        :param thumbnail: storage.thumbnail recordset
        :param image_relation: product.image.relation recordset
        :return: dict
        """
        self.ensure_one()
        values = super()._prepare_data_resize(
            thumbnail=thumbnail, image_relation=image_relation
        )
        url_key = "src"
        url = values.get(url_key)
        if url and "backend_id" in self._fields:
            values.update({url_key: self.backend_id._replace_by_proxy(url)})
        return values
