# Copyright 2023 Akretion (https://www.akretion.com).
# @author Matthieu SAISON <matthieu.saison@akretion.com>
# License AGPL-3.0 or later (https: //www.gnu.org/licenses/agpl).

import logging

from odoo import api, models

from odoo.addons.shopinvader_product_binding.hooks import PRODUCT_XML_IDS
from odoo.addons.shopinvader_restapi.hooks import RESTAPI_XML_IDS

_logger = logging.getLogger(__name__)


def mapped_xml_id(xmlid):
    # fix the existing ref to shopinvader by new name
    module, name = xmlid.split(".")
    if module == "shopinvader":
        if name in PRODUCT_XML_IDS:
            _logger.warning(
                f"Old name for shopinvader is used: {xmlid} \n"
                "Please rename module ref to "
                "shopinvader_product_binding"
            )
            xmlid = f"shopinvader_product_binding.{name}"
        elif name in RESTAPI_XML_IDS:
            xmlid = f"shopinvader_restapi.{name}"
            _logger.warning(
                f"Old name for shopinvader is used: {xmlid} \n"
                "Please rename module ref to shopinvader_restapi"
            )
    return xmlid


class IrModelData(models.Model):
    _inherit = "ir.model.data"

    @api.model
    def xmlid_lookup(self, xmlid):
        xmlid = mapped_xml_id(xmlid)
        return super().xmlid_lookup(xmlid)


class IrFieldsConverter(models.AbstractModel):
    _inherit = "ir.fields.converter"

    def _xmlid_to_record_id(self, xmlid, model):
        xmlid = mapped_xml_id(xmlid)
        return super()._xmlid_to_record_id(xmlid, model)
