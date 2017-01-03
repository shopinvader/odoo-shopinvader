# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp.addons.connector.backend import Backend
from openerp.addons.connector_nosql_locomotivecms.backend import (
    locomotivecms_v3)


shoptor = Backend(parent=locomotivecms_v3)
""" Shoptor Backend"""

shoptor_v1 = Backend(parent=shoptor, version='shoptor_v1')
""" Shoptor V1 Backend"""
