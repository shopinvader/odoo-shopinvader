# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.addons.connector.event import (on_record_write,
                                            on_record_create,
                                            on_record_unlink
                                            )
from openerp.addons.connector_generic.consumer import Consumer
from openerp.addons.connector_locomotivecms.connector import get_environment
from openerp.addons.connector_locomotivecms.unit.exporter import export_record
from openerp.addons.connector_locomotivecms.unit.deleter import (
    export_delete_record)


@on_record_create(model_names=[
    'locomotivecms.product',
    'locomotivecms.image',
    ])
def delay_export(session, model_name, record_id, vals=None):
    with session.change_context(connector_force_export=True):
        consumer = Consumer(session, get_environment, model_name, record_id)
        consumer.delay_export(export_record, vals=vals)


@on_record_write(model_names=[
    'locomotivecms.product',
    'locomotivecms.image',
    ])
def delay_export(session, model_name, record_id, vals=None):
    consumer = Consumer(session, get_environment, model_name, record_id)
    consumer.delay_export(export_record, vals=vals)


@on_record_write(model_names=[
    'product.template',
    'base_multi_image.image',
    ])
def delay_export_all_binding(session, model_name, record_id, vals=None):
    consumer = Consumer(session, get_environment, model_name, record_id)
    consumer.delay_export_all_binding(
        export_record, 'locomotivecms_bind_ids', vals=vals)


@on_record_unlink(model_names=[
    'locomotivecms.product',
    'locomotivecms.image',
    ])
def delay_unlink(session, model_name, record_id):
    consumer = Consumer(session, get_environment, model_name, record_id)
    consumer.delay_unlink(export_delete_record)


@on_record_unlink(model_names=[
    'product.template',
    'base_multi_image.image',
])
def delay_unlink_all_option_binding(session, model_name, record_id):
    consumer = Consumer(session, get_environment, model_name, record_id)
    consumer.delay_unlink_all_binding(
        export_delete_record, 'locomotivecms_bind_ids')
