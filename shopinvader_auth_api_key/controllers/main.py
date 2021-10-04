# Copyright 20201 ACSONE SA/NV (http://acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.base_rest.controllers import main


class InvaderController(main.RestController):

    _root_path = "/shopinvader/"
    _collection_name = "shopinvader.backend"
    _default_auth = "api_key"
    _default_save_session = False
    _component_context_provider = "shopinvader_auth_api_key_context_provider"
