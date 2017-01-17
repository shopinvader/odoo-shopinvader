# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp.addons.connector_locomotivecms.backend import locomotive
from openerp.addons.connector_locomotivecms.unit.exporter import (
    LocomotiveExporter)


@locomotive
class ProductExporter(LocomotiveExporter):
    _model_name = 'locomotive.product'

    def _export_dependencies(self):
        exporter = self.unit_for(AssetExporter, model='locomotive.image')
        for image in self.binding_record.image_ids:
            for binding in image.locomotive_bind_ids:
                if not binding.external_id\
                        and binding.backend_id == self.backend_record:
                    exporter.run(binding.id)
        for link in self.binding_record.media_link_ids:
            for media in link.media_ids:
                self._export_dependency(media, 'locomotive.media')


@locomotive
class CategExporter(LocomotiveExporter):
    _model_name = 'locomotive.category'


@locomotive
class AssetExporter(LocomotiveExporter):
    _model_name = [
        'locomotive.image',
        'locomotive.media',
    ]

    def _run(self, fields=None):
        res = super(AssetExporter, self)._run(fields=fields)
        self.binding_record.url = self.result['url']
        return res
