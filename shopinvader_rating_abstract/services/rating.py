# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, exceptions

from odoo.addons.component.core import AbstractComponent


class RatingAbstractService(AbstractComponent):
    """
    Shopinvader abstract service to create/edit/delete customers ratings

    To create a new service using this abstract you only need to add the following
    in your own module:

    class YourRatingService(Component):
        _inherit = "shopinvader.abstract.rating.service"
        _name = "your.service.name"
        _usage = "your.usage"
        _description = "your service description"
        _rating_model: The model you want to add ratings to
    """

    _name = "shopinvader.abstract.rating.service"
    _inherit = "base.shopinvader.service"
    _expose_model = "rating.rating"
    _rating_model = None

    def _prepare_params(self, params):
        record = self._get_record(params.pop("id"))
        lang = self.env["res.lang"].search(
            [("code", "=", self.env.context["lang"])], limit=1
        )
        model = self.env["ir.model"].search([("model", "=", record._name)], limit=1)
        params.update(
            {
                "shopinvader_backend_id": self.shopinvader_backend.id,
                "partner_id": self.partner_user.id,
                "lang_id": lang.id,
                "res_id": record.id,
                "res_model": record._name,
                "res_model_id": model.id,
                "consumed": True,
            }
        )
        return params

    def _get_record(self, record_id):
        return self.env[self._rating_model].browse(record_id)

    # pylint: disable=W8106
    def create(self, **params):
        """
        Create a new rating
        :param dict/json
        :return: dict/json
        """

        if not self._is_logged_in():
            raise exceptions.UserError(_("Must be authenticated to create a rating"))
        vals = self._prepare_params(params)
        record = self.env[self._expose_model].create(vals)
        record.synchronize_rating()
        record._send_notification("rating_created")
        return {"created": True, "message": "rating created"}

    def update(self, _id, **params):
        """
        Update an existing rating
        :param _id: int
        :param params: dict/json
        :return: dict/json
        """
        record = self.env["rating.rating"].browse(_id)
        if record.exists() and self.partner.id == record.partner_id.id:
            record.write(params)
            record.synchronize_rating()
            return {"updated": True, "message": "The rating has been updated"}
        raise exceptions.UserError(
            _("The record does not exist or you cannot update it")
        )

    def delete(self, _id):
        """
        Delete an existing record
        :param _id: int
        :return: dict/json
        """
        record = self.env["rating.rating"].browse(_id)
        if record.exists() and self.partner.id == record.partner_id.id:
            record.active = False
            record.synchronize_rating()
            return {"deleted": True, "message": "The rating has been deleted"}
        raise exceptions.UserError(
            _("The record does not exist or you cannot delete it")
        )

    def _validator_create(self):
        res = {
            "id": {"type": "integer", "required": True},
            "rating": {"type": "integer", "required": True},
            "feedback": {"type": "string", "required": False},
        }
        return res

    def _validator_update(self):
        res = {
            "rating": {"type": "integer", "required": True},
            "feedback": {"type": "string", "required": False},
        }
        return res

    def _validator_return_create(self):
        schema = {"created": {"type": "boolean"}, "message": {"type": "string"}}
        return schema

    def _validator_return_update(self):
        schema = {"updated": {"type": "boolean"}, "message": {"type": "string"}}
        return schema

    def _validator_return_delete(self):
        schema = {"deleted": {"type": "boolean"}, "message": {"type": "string"}}
        return schema
