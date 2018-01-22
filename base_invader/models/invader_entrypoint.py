# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager

from odoo.addons.component.core import WorkContext

from odoo import api, fields, models


class _PseudoCollection(object):
    def __init__(self, name, env):
        self._name = name
        self.env = env


class InvaderEntrypoint(models.Model):
    """ The model on which components services are subscribed

       To be usable, you must inherit from the model to add into the colection
       the name on which your components services are registered.

       Example::

           class InvaderEntrypoint(models.Model):
               _inherit = 'invader.entrypoint'

               collection = fields.Selection(
                   selection_add=('shopinvader', 'Shopinvader Services'))


           class ShopinvaderPingService(Component):
               _name = 'shopinvader.ping.service'
               _inherit = 'invader.service'
               _collection = 'shopinvader'  # name of the collection

               @secure_params
               def get(self, params):
                   return {
                       'response':
                       'GET called with message ' + params['message']}
                   # ...

           from odoo.addons.base_invader.controllers import main
           from odoo.http import route

           class InvaderController(main.InvaderController):

           # ping
           @route('/shop/ping', methods=['GET', 'POST', 'PUT', 'DELETE'],
               auth="api_key", csrf=False)
           def ping(self, **params):
               return self.send_to_service('ping.service', params)

       """

    _name = 'invader.entrypoint'
    _description = 'Invader REST Services Entry point'

    name = fields.Char(
        required=True
    )
    api_key = fields.Char(
        help=("This is the API key that you need to add in HTTP request "
              "hearders in order to give access to odoo services")
    )
    collection = fields.Selection(
        [('default.service.collection', 'Default service collection')],
        required=True,
        default='default.service.collection',
    )

    @contextmanager
    @api.multi
    def work_on(self, model_name, **kwargs):
        """ Entry-point for the components, context manager

        Start a work using the components on the model for the given
        collection.
        Any keyword argument will be assigned to the work context.
        See documentation of :class:`odoo.addons.component.core.WorkContext`.

        It is a context manager, so you can attach objects and clean them
        at the end of the work session, such as::

            @contextmanager
            @api.multi
            def work_on(self, model_name, **kwargs):
                self.ensure_one()
                magento_location = MagentoLocation(
                    self.location,
                    self.username,
                    self.password,
                )
                # We create a Magento Client API here, so we can create the
                # client once (lazily on the first use) and propagate it
                # through all the sync session, instead of recreating a client
                # in each backend adapter usage.
                with MagentoAPI(magento_location) as magento_api:
                    _super = super(MagentoBackend, self)
                    # from the components we'll be able to do:
                    # self.work.magento_api
                    with _super.work_on(
                            model_name, magento_api=magento_api, **kwargs
                            ) as work:
                        yield work

        """
        self.ensure_one()
        collection = _PseudoCollection(self.collection, self.env)
        yield WorkContext(
            model_name=model_name, collection=collection, **kwargs)
