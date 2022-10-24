# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, exceptions

from odoo.addons.component.core import AbstractComponent


class ProductRatingUpvoteService(AbstractComponent):
    """
    This abstract service allows the upvoting of user ratings
    """

    _name = "shopinvader.rating.upvote.service"
    _description = __doc__

    def upvote(self, _id):
        """
        Upvote an existing rating
        :param _id: int
        :return: dict/json
        """
        record = self.env["rating.rating"].browse(_id)
        if (
            record.exists()
            and self.partner != record.partner_id
            and self.partner not in record.partner_ids
        ):
            record.write({"partner_ids": [(4, self.partner.id)]})
            record.synchronize_rating()
            return {"upvoted": True, "message": "The rating has been upvoted"}
        raise exceptions.UserError(
            _("The record does not exist or you cannot upvote it")
        )

    def _validator_upvote(self):
        return {}

    def _validator_return_upvote(self):
        schema = {"upvoted": {"type": "boolean"}, "message": {"type": "string"}}
        return schema
