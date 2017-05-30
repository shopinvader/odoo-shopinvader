# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def post_init_hook(cr, registry):
    config_obj = registry['sale.config.settings']
    config_id = config_obj.create(cr, 1, {'group_discount_per_so_line': True})
    config_obj.execute(cr, 1, [config_id])
