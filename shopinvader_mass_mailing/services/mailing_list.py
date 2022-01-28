# Copyright 2021 Camptocamp (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component


class MailingListsService(Component):
    """Shopinvader Service to manage mailing list subscriptions."""

    _name = "shopinvader.mailing.lists.service"
    _inherit = "base.shopinvader.service"
    _usage = "mailing_lists"
    _expose_model = "mailing.list"
    _description = __doc__

    @property
    def _exposed_model(self):
        # As auth is "public" the tech user is not taken into account here
        return super()._exposed_model.sudo()

    @restapi.method(
        [(["/<int:id>/get", "/<int:id>"], "GET")],
        input_param=restapi.CerberusValidator("_validator_get"),
        output_param=restapi.CerberusValidator("_validator_return_get"),
        auth="public",
    )
    def get(self, _id, **params):
        """Get a mailing list"""
        record = self._get(_id)
        return self._to_json(record, one=True)

    @restapi.method(
        [(["/", "/search"], "GET")],
        input_param=restapi.CerberusValidator("_validator_search"),
        output_param=restapi.CerberusValidator("_validator_return_search"),
        auth="public",
    )
    def search(self, **params):
        """Search mailing lists"""
        return self._paginate_search(**params)

    @restapi.method(
        [(["/<int:id>/subscribe"], "POST")],
        input_param=restapi.CerberusValidator("_validator_subscribe"),
        output_param=restapi.CerberusValidator("_validator_return_subscribe"),
        auth="public",
    )
    def subscribe(self, _id, **params):
        """Subscribe email to a mailing list"""
        record = self._get(_id)
        return self._subscribe(record, **params)

    @restapi.method(
        [(["/<int:id>/unsubscribe"], "POST")],
        input_param=restapi.CerberusValidator("_validator_unsubscribe"),
        output_param=restapi.CerberusValidator("_validator_return_subscribe"),
        auth="public",
    )
    def unsubscribe(self, _id, **params):
        """Unsubscribe email from a mailing list"""
        record = self._get(_id)
        return self._unsubscribe(record, **params)

    @restapi.method(
        [(["/unsubscribe_all"], "POST")],
        input_param=restapi.CerberusValidator("_validator_unsubscribe_all"),
        output_param=restapi.CerberusValidator("_validator_return_unsubscribe_all"),
        auth="public",
    )
    def unsubscribe_all(self, **params):
        """Unsubscribe email from all mailing lists"""
        records = self._exposed_model.search(self._get_base_search_domain())
        return self._unsubscribe(records, **params)

    def _subscribe(self, records, **params):
        """Subscribe email to the given mailing lists"""
        contact = self._get_mailing_contact(**params)
        for record in records:
            subscription = self._get_mailing_subscription(record, contact, **params)
            if subscription.opt_out:
                subscription.opt_out = False
        return {"success": True}

    def _unsubscribe(self, records, **params):
        """Unsubscribe email from the given mailing lists"""
        __, email = self.env["mailing.contact"].sudo().get_name_email(params["email"])
        Subscription = self.env["mailing.contact.subscription"].sudo()
        subscriptions = Subscription.search(
            [
                ("contact_id.email_normalized", "=", email),
                ("list_id", "in", records.ids),
                ("opt_out", "=", False),
            ],
        )
        if not subscriptions:
            return {"success": False, "message": "Not subscribed"}
        subscriptions.opt_out = True
        return {"success": True}

    def _prepare_mailing_contact_vals(self, name, email, params):
        """Override this method if you need custom mailing.contact values"""
        return {
            "name": name,
            "email": email,
        }

    def _prepare_mailing_subscription_vals(self, record, contact, params):
        """Override this method if you need custom mailing.subscription values"""
        return {
            "list_id": record.id,
            "contact_id": contact.id,
        }

    def _get_mailing_contact(self, email, create_if_not_found=True, **params):
        """Gets or creates a mailing contact from an email address"""
        Contact = self.env["mailing.contact"].sudo()
        name, email = Contact.get_name_email(email)
        contact = Contact.search(
            [
                ("email_normalized", "=", email),
            ],
            limit=1,
        )
        if not contact and create_if_not_found:
            vals = self._prepare_mailing_contact_vals(name, email, params)
            contact = Contact.create(vals)
        return contact

    def _get_mailing_subscription(
        self, record, contact, create_if_not_found=True, **params
    ):
        """Gets or creates a mailing subscription from a mailing list and a contact"""
        Subscription = self.env["mailing.contact.subscription"].sudo()
        subscription = Subscription.search(
            [
                ("list_id", "=", record.id),
                ("contact_id", "=", contact.id),
            ],
            limit=1,
        )
        if not subscription and create_if_not_found:
            vals = self._prepare_mailing_subscription_vals(record, contact, params)
            subscription = Subscription.create(vals)
        return subscription

    def _is_user_subscribed(self, record):
        """Returns if True if the user is subscribed to the given mailing list"""
        record.ensure_one()
        email = self.work.partner_user.email_normalized
        if not email:
            return False
        return bool(
            self.env["mailing.contact.subscription"]
            .sudo()
            .search_count(
                [
                    ("contact_id.email_normalized", "=", email),
                    ("list_id", "=", record.id),
                    ("opt_out", "=", False),
                ],
            )
        )

    def _get_base_search_domain(self):
        return [("is_public", "=", True)]

    def _json_parser(self):
        res = [
            "id",
            "name",
        ]
        # If the user is authenticated, add the subscription status
        if self._is_logged_in():
            res.append(
                ("id:subscribed", lambda rec, fname: self._is_user_subscribed(rec))
            )
        return res

    def _to_json(self, records, one=False, **kw):
        return records.jsonify(self._json_parser(), one=one)

    def _get_schema(self):
        return {
            "id": {
                "type": "integer",
                "required": True,
                "nullable": False,
            },
            "name": {
                "type": "string",
                "required": True,
                "nullable": False,
            },
            "subscribed": {
                "type": "boolean",
                "required": False,
            },
        }

    def _validator_get(self):
        return {}

    def _validator_return_get(self):
        return self._get_schema()

    def _validator_search(self):
        return super()._default_validator_search()

    def _validator_return_search(self):
        return {
            "size": {"type": "integer", "required": True},
            "data": {
                "type": "list",
                "required": True,
                "nullable": False,
                "schema": {
                    "type": "dict",
                    "schema": self._get_schema(),
                },
            },
        }

    def _get_validator_email(self):
        # If the user is authenticated, email defaults to the current user's email.
        # Effectively, this parameter can be ignored on authenticated requests.
        return {
            "email": {
                "type": "string",
                "required": True,
                "empty": False,
                "nullable": False,
                "default_setter": lambda doc: self.work.partner_user.email_normalized,
            },
        }

    def _get_validator_return_success(self):
        return {
            "success": {"type": "boolean", "required": True},
            "message": {"type": "string", "required": False},
        }

    def _validator_subscribe(self):
        return self._get_validator_email()

    def _validator_return_subscribe(self):
        return self._get_validator_return_success()

    def _validator_unsubscribe(self):
        return self._get_validator_email()

    def _validator_return_unsubscribe(self):
        return self._get_validator_return_success()

    def _validator_unsubscribe_all(self):
        return self._get_validator_email()

    def _validator_return_unsubscribe_all(self):
        return self._get_validator_return_success()
