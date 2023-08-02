# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=method-required-super


from odoo.addons.shopinvader_v1_base.tests.common import CommonMixin


class CommonMixin(CommonMixin):
    @staticmethod
    def _setup_backend(cls):
        super()._setup_backend(cls)
        cls.backend.bind_all_product()
