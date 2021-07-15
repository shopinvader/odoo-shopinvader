# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from functools import wraps

from odoo import _, exceptions
from odoo.osv import expression

from odoo.addons.base_rest.components.service import to_bool, to_int
from odoo.addons.component.core import Component


# TODO: move it to core module
def protect_by_invader_user(checker_name):
    """Decorator to protect endpoints by a check on current invader partner user.

    :param checker_name: a method or attribute on shopinvader.partner model or service
    """

    def _protect(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            service = args[0]
            user = service.invader_partner_user
            if user is None:
                raise exceptions.AccessError(_("User not authenticated"))
            if checker_name in user._fields:
                checker = user[checker_name]
            elif hasattr(user, checker_name):
                checker = getattr(user, checker_name)
            else:
                # let if fail badly if not found
                checker = getattr(service, checker_name)
            result = checker() if callable(checker) else checker
            if not result:
                raise exceptions.AccessError(_("User not allowed"))
            return func(*args, **kwargs)

        return wrapped

    return _protect


class UsersService(Component):
    """Manage customers' users.

    This service provides endpoints to allow customers
    to manage their users straight from the frontend.
    """

    _name = "shopinvader.users.service"
    _inherit = "base.shopinvader.service"
    _usage = "users"
    _expose_model = "shopinvader.partner"
    _description = __doc__

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it !

    @protect_by_invader_user("is_users_manager")
    def search(self, **params):
        return self._paginate_search(**params)

    # pylint: disable=W8106
    @protect_by_invader_user("is_users_manager")
    def create(self, **params):
        vals = self._prepare_params(params.copy())
        record = self.env[self._expose_model].create(vals)
        self._post_create(record)
        return {"data": self._to_json(record, one=True)}

    @protect_by_invader_user("is_users_manager")
    def update(self, _id, **params):
        # TODO: prevent update of records not in the same hierarchy?
        record = self._get(_id)
        record.write(self._prepare_params(params.copy(), mode="update"))
        self._post_update(record)
        return self.search()

    @protect_by_invader_user("is_users_manager")
    def delete(self, _id):
        # TODO: add test
        if _id == self.invader_partner_user.id:
            raise exceptions.UserError(_("You cannot delete your own user"))
        binding = self._get(_id)
        self._delete(binding)
        return self.search()

    def _post_create(self, record):
        pass

    def _post_update(self, record):
        pass

    def _validator_search(self):
        return {
            "id": {"coerce": to_int, "type": "integer"},
            "per_page": {
                "coerce": to_int,
                "nullable": True,
                "type": "integer",
            },
            "page": {"coerce": to_int, "nullable": True, "type": "integer"},
            "scope": {"type": "dict", "nullable": True},
        }

    def _validator_create(self):
        return {
            "name": {"type": "string", "required": True},
            "email": {"type": "string", "required": True},
            "can_manage_users": {
                "type": "boolean",
                "coerce": to_bool,
                "nullable": True,
            },
            "parent_id": {
                "type": "integer",
                "coerce": to_int,
                "nullable": True,
            },
        }

    def _validator_update(self):
        res = self._validator_create()
        # Prevent email/login update
        res.pop("email", None)
        for key in res:
            if "required" in res[key]:
                del res[key]["required"]
        return res

    def _get_base_search_domain(self):
        if not self._is_logged_in() or not self.invader_partner_user.is_users_manager:
            return expression.FALSE_DOMAIN
        # Simple users w/ delegated permissions
        # can see only records they own.
        delegated = (
            self.invader_partner_user.is_invader_user
            and self.invader_partner_user.can_manage_users
        )
        return self.invader_partner_user._make_partner_domain(
            "main_partner_id" if not delegated else "parent_id"
        )

    def _prepare_params(self, params, mode="create"):
        # Always enforce the backend
        params["backend_id"] = self.shopinvader_backend.id
        parent_id = params.pop("parent_id", None)
        if parent_id:
            # Users can be created only in the same hierarchy
            record = (
                self.env["res.partner"]
                .browse(parent_id)
                .filtered_domain(
                    [
                        (
                            "id",
                            "child_of",
                            self.invader_partner_user.main_partner_id.id,
                        )
                    ]
                )
                .exists()
            )
            if not record:
                parent_id = None
        params["parent_id"] = parent_id or self.partner_user.id
        return params

    def _to_json(self, records, one=None, **kw):
        return records.jsonify(self._json_parser(), one=one)

    def _json_parser(self):
        return [
            "id",
            "name",
            "email",
            "can_manage_users",
            ("parent_id", lambda rec, fname: rec[fname].id),
        ]

    def _delete(self, binding):
        partner = binding.record_id
        other_bindings = (
            partner.shopinvader_bind_ids - binding
            | partner.child_ids.shopinvader_bind_ids
        )
        if not other_bindings:
            # Just one shopinvader user tied to it
            partner.active = False
        binding.unlink()
