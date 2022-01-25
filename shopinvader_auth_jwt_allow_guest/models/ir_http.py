from odoo import models
from odoo import SUPERUSER_ID, api, models, registry as registry_get
from odoo.http import request
from odoo.addons.auth_jwt.exceptions import (
    UnauthorizedInvalidToken,
    JwtValidatorNotFound,
)


class IrHttpJwt(models.AbstractModel):

    _inherit = "ir.http"

    @classmethod
    def _auth_method_jwt(cls, validator_name=None):
        # This allow to check all jwt validators
        assert request.db
        if validator_name:
            return super()._auth_method_jwt(validator_name)

        registry = registry_get(request.db)
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            validator_names = env["auth.jwt.validator"].search([]).mapped("name")

        if not len(validator_names):
            raise JwtValidatorNotFound()
        for validator_name in validator_names:
            try:
                super()._auth_method_jwt(validator_name)
                return
            except UnauthorizedInvalidToken:
                continue
        raise UnauthorizedInvalidToken()
