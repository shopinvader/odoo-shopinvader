# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.addons.base_invader.controllers import main
from odoo.http import request

_logger = logging.getLogger(__name__)


class InvaderController(main.InvaderController):

    def _get_component_context(self):
        """
        This method can be inherited to add parameter into the component
        context
        :return: dict of key value.
        """
        params = super(InvaderController, self)._get_component_context()
        params['partner'] =request.partner
        return params
