# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import functools
from odoo.addons.queue_job.job import related_action
from .unit.binder import LocomotiveBinder

# TODO MIGRATE
#unwrap_binding = functools.partial(related_action.unwrap_binding,
#                                   binder_class=LocomotiveBinder)
