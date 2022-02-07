from odoo import SUPERUSER_ID, api, models, registry as registry_get
from odoo.http import request

from odoo.addons.auth_jwt.exceptions import JwtValidatorNotFound


class CompositeJwtError(Exception):
    pass


class IrHttpJwt(models.AbstractModel):

    _inherit = "ir.http"

    @classmethod
    def _auth_method_jwt(cls, validator_name=None):
        # This allows to check all jwt validators
        assert request.db
        assert not request.uid
        assert not request.session.uid

        token = cls._get_bearer_token()

        registry = registry_get(request.db)
        exceptions = {}
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            validators = env["auth.jwt.validator"].search([])

            if not len(validators):
                raise JwtValidatorNotFound()

            for validator in validators:
                try:
                    payload = validator._decode(token)
                    uid = validator._get_and_check_uid(payload)
                    partner_id = validator._get_and_check_partner_id(payload)
                except Exception as e:
                    exceptions[validator_name] = e
                    continue

                request.uid = uid  # this resets request.env
                request.jwt_payload = payload
                request.jwt_partner_id = partner_id
                break
            else:
                if len(exceptions) == 1:
                    raise list(exceptions.values())[0]

                raise CompositeJwtError(exceptions)
