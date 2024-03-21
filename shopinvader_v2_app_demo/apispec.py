# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# pylint: disable=missing-return

from apispec import BasePlugin


class RestMethodSecurityPlugin(BasePlugin):
    def __init__(self, service):
        super(RestMethodSecurityPlugin, self).__init__()
        self._service = service

    def init_spec(self, spec):
        super(RestMethodSecurityPlugin, self).init_spec(spec)
        self.spec = spec
        self.openapi_version = spec.openapi_version
        jwt_scheme = {
            "type": "oauth2",
            "flows": {
                "authorizationCode": {
                    "authorizationUrl": "https://keycloak.demo16.shopinvader.com/"
                    "auth/realms/master/protocol/openid-connect/auth",
                    "tokenUrl": "https://keycloak.demo16.shopinvader.com/"
                    "auth/realms/master/protocol/openid-connect/token",
                    "scopes": {"openid": "", "email": "", "profile": ""},
                }
            },
            "name": "oauth2",
        }
        spec.components.security_scheme("oauth2", jwt_scheme)

    def operation_helper(self, path=None, operations=None, **kwargs):
        routing = kwargs.get("original_routing")
        if not routing:
            super(RestMethodSecurityPlugin, self).operation_helper(
                path, operations, **kwargs
            )
        if not operations:
            return
        auth = routing.get("auth", self.spec._params.get("default_auth"))
        if auth and auth.startswith("jwt"):
            for _method, params in operations.items():
                security = params.setdefault("security", [])
                security.append({"oauth2": []})
