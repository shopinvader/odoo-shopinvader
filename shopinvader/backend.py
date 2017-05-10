# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp.addons.connector.backend import Backend
from openerp.addons.connector_locomotivecms.backend import locomotive


shopinvader = Backend(parent=locomotive, version='shopinvader')
""" Shopinvader Backend"""

shopinvader_v1 = Backend(parent=shopinvader, version='shopinvader_v1')
