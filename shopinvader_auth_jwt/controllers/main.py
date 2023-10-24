# Copyright 2021 ACSONE SA/NV (http://acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.base_rest.controllers import main


class InvaderController(main.RestController):

    _root_path = "/shopinvader_jwt/"
    _collection_name = "shopinvader.backend"
    _default_auth = "jwt"
    _default_save_session = False
    _default_cors = True
    _component_context_provider = "shopinvader_auth_jwt_context_provider"
