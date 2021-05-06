# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from contextlib import contextmanager

from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext


def get_partner_work_context(shopinvader_partner):
    """Retrieve service work context for given shopinvader.partner
    """
    ctx = {}
    ctx["invader_partner"] = shopinvader_partner
    ctx["invader_partner_user"] = shopinvader_partner
    # TODO: `partner` and `partner_user` could be abandoned as soon as
    # all `shopinvader` modules stop relying on `self.partner`.
    partner_user = shopinvader_partner.record_id
    ctx["partner_user"] = partner_user
    # The partner user for the main account or for sale order may differ.
    partner_shop = partner_user.get_shop_partner(
        shopinvader_partner.backend_id
    )
    ctx["partner"] = partner_shop
    if partner_shop != partner_user:
        # Invader partner must represent the same partner as the shop
        invader_partner_shop = partner_shop._get_invader_partner(
            shopinvader_partner.backend_id
        )
        if invader_partner_shop:
            ctx["invader_partner"] = invader_partner_shop
    return ctx


def load_partner_work_ctx(service, invader_partner, force=False):
    """Update work context for given service loading given invader partner ctx."""
    params = get_partner_work_context(invader_partner)
    update_work_ctx(service, params, force=force)


def reset_partner_work_ctx(service):
    """Update work context flushing all partner keys."""
    defaults = {}
    partner_work_context_defaults(
        service.env, service.shopinvader_backend, defaults
    )
    update_work_ctx(service, defaults, force=True)


def update_work_ctx(service, params, force=False):
    """Update work context for given service."""
    for k, v in params.items():
        # The attribute on the service could be None or empty recordset.
        if force or not getattr(service.work, k, None):
            setattr(service.work, k, v)


def partner_work_context_defaults(env, backend, params):
    """Inject defaults as these keys are mandatory for work ctx."""
    if params.get("partner") and not params.get("partner_user"):
        params["partner_user"] = params["partner"]
    for k in ("partner", "partner_user"):
        if not params.get(k):
            params[k] = env["res.partner"].browse()
        if not params.get("invader_" + k):
            params["invader_" + k] = params[k]._get_invader_partner(backend)


@contextmanager
def work_on_service(env, **params):
    """Work on a shopinvader service."""
    collection = _PseudoCollection("shopinvader.backend", env)
    yield WorkContext(
        model_name="rest.service.registration", collection=collection, **params
    )


@contextmanager
def work_on_service_with_partner(env, invader_partner, **kw):
    """Work on a shopinvader service using given shopinvader.partner."""
    params = get_partner_work_context(invader_partner)
    params["shopinvader_backend"] = invader_partner.backend_id
    params.update(kw)
    with work_on_service(env, **params) as work:
        yield work
