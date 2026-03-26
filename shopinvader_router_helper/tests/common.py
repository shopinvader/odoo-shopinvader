# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models

from odoo.addons.fastapi.tests.common import FastAPITransactionCase


class CommonFastAPIEndpointCase(FastAPITransactionCase):
    @classmethod
    def setUpEndpoint(cls, endpoint, api_user=None, default_partner=None):
        cls.endpoint = cls.env.ref(endpoint) if isinstance(endpoint, str) else endpoint

        cls.env = cls.env(
            context=dict(
                **cls.env.context,
                # Since env often comes from the authenticated_partner which
                # doesn't use odoo_env dependency in tests we need to set
                # the context explicitly for all the cases:
                **cls.endpoint._get_app_context(),
            )
        )

        # Set up endpoint app
        cls.default_fastapi_app = cls.endpoint._get_app()

        # Set up endpoint dependency overrides except for partners
        # (These are set by default_fastapi_authenticated_partner or directly
        # partner in _create_test_client)
        cls.default_fastapi_dependency_overrides = {
            k: v
            for k, v in cls.default_fastapi_app.dependency_overrides.items()
            if k.__name__
            not in (
                "authenticated_partner_impl",
                "optionally_authenticated_partner_impl",
            )
        }

        if api_user:
            api_user = cls.env.ref(api_user) if isinstance(api_user, str) else api_user
            cls.default_fastapi_running_user = api_user

        if default_partner:
            cls.partner = (
                cls.env.ref(default_partner)
                if isinstance(default_partner, str)
                else default_partner
            )
            cls.default_fastapi_authenticated_partner = cls.partner


def setup_models(env, module):
    # Temporary add models to registry
    models = env.registry.load(
        env.cr,
        type("_name_getter", (object,), {"name": "shopinvader_router_helper"}),
    )
    env.registry.setup_models(env.cr)
    env.registry.init_models(env.cr, models, {"module": "shopinvader_router_helper"})


def unsetup_models(env, module):
    # Remove models from registry
    for model in models.MetaModel.module_to_models[module]:
        del env.registry[model._name]
