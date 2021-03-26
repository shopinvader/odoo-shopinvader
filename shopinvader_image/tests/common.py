# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2020 Camptocamp (http://www.camptocamp.com)
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader.tests.common import ProductCommonCase
from odoo.addons.storage_image_product.tests.common import ProductImageCommonCase


class TestShopinvaderImageCase(ProductCommonCase, ProductImageCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ProductImageCommonCase.setUpClass()
        cls.logo = cls.env["product.image.relation"].create(
            {"product_tmpl_id": cls.template.id, "image_id": cls.logo_image.id}
        )
        cls.image_bk = cls.env["product.image.relation"].create(
            {
                "product_tmpl_id": cls.template.id,
                "image_id": cls.black_image.id,
                "attribute_value_ids": [
                    (
                        6,
                        0,
                        [cls.env.ref("product.product_attribute_value_4").id],
                    )
                ],
            }
        )
