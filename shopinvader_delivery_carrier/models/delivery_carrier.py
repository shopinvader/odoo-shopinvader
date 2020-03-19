# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from contextlib import contextmanager

from odoo import api, models


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    @contextmanager
    def _simulate_delivery_cost(self, partner):
        """
        Change the env mode (draft) to avoid real update on the partner.
        Then, restore the partner with previous values.
        :param partner: res.partner recordset
        :return:
        """
        partner.read(["country_id", "zip"])
        partner_values = partner._convert_to_write(partner._cache)
        with partner.env.do_in_draft():
            yield
            # Restore values
            partner.update(partner_values)

    @api.model
    def _get_country_from_context(self):
        """
        Load the country from context
        :return: res.country recordset
        """
        country_id = self.env.context.get("delivery_force_country_id", 0)
        return self.env["res.country"].browse(country_id)

    @api.model
    def _get_zip_from_context(self):
        """
        Load the zip code from context
        :return: str
        """
        return self.env.context.get("delivery_force_zip_code", "")

    @api.multi
    def available_carriers(self, contact):
        """
        Inherit the function to force some values on the given contact
        (only in cache).
        :param contact: res.partner recordset
        :return: False or self
        """
        country = self._get_country_from_context()
        zip_code = self._get_zip_from_context()
        if country or zip_code:
            with self._simulate_delivery_cost(contact):
                # Edit country and zip
                # Even if some info are not provided, we have to fill them
                # Ex: if the zip code is not provided, we have to do the
                # simulation with an empty zip code on the partner. Because his
                # current zip could be related to another country and simulate
                # a wrong price.
                contact.update({"country_id": country.id, "zip": zip_code})
                result = super(DeliveryCarrier, self).available_carriers(
                    contact
                )
        else:
            result = super(DeliveryCarrier, self).available_carriers(contact)
        return result
