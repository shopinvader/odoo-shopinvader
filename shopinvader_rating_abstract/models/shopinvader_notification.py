# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models
from odoo.tools.translate import _


class ShopinvaderNotification(models.Model):
    _inherit = ["shopinvader.notification", "rest.service.registration"]
    _name = "shopinvader.notification"

    def _get_selection_rating(self):
        """
        Get all shopinvader services and filter for the ones that inherit from rating abstract.
        For each service create 2 types of notifications:
            - when a user has created a news rating (rating_created_model_name)
            - when the rating moderator published a response
              on a rating (rating_publisher_response_model_name)
        """
        shopinvader_services = self._get_services("shopinvader.backend")
        abstract_rating_childs = filter(
            lambda x: "shopinvader.abstract.rating.service" in x._inherit,
            shopinvader_services,
        )
        notifications = {}
        for service in abstract_rating_childs:
            rating_model = self.env[service._rating_model]
            notifications["rating_created_{}".format(rating_model._table)] = {
                "name": _(
                    "New rating created for {}".format(rating_model._description)
                ),
                "model": "rating.rating",
            }

            notifications[
                "rating_publisher_response_{}".format(rating_model._table)
            ] = {
                "name": _(
                    "Publisher responded to a rating for {}".format(
                        rating_model._description
                    )
                ),
                "model": "rating.rating",
            }
        return notifications

    def _get_all_notification(self):
        res = super()._get_all_notification()
        res.update(self._get_selection_rating())
        return res
