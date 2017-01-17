# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import functools
from openerp.addons.connector import related_action
from .unit.binder import LocomotiveBinder

unwrap_binding = functools.partial(related_action.unwrap_binding,
                                   binder_class=LocomotiveBinder)
