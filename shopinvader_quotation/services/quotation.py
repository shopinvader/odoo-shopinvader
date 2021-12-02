# Copyright 2016 Akretion (http://www.akretion.com)
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# Copyright 2021 Camptocamp (http://www.camptocamp.com)
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component


class QuotationService(Component):
    _inherit = [
        "shopinvader.abstract.sale.service",
        "abstract.shopinvader.download",
    ]
    _name = "shopinvader.quotation.service"
    _usage = "quotations"
    _expose_model = "sale.order"

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it !

    def get(self, _id):
        order = self._get(_id)
        return self._to_json(order)[0]

    def confirm(self, _id):
        order = self._get(_id)
        self._confirm(order)
        return self.component(usage="sales").get(order.id)

    def search(self, **params):
        return self._paginate_search(**params)

    def _get_report_action(self, target, params=None):
        """
        Get the action/dict to generate the report
        :param target: recordset
        :param params: dict
        :return: dict/action
        """
        return self.env.ref("sale.action_report_saleorder").report_action(
            target, config=False
        )

    # Validator

    def _validator_get(self):
        return {}

    def _validator_confirm(self):
        return {}

    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

    def _get_base_search_domain(self):
        show_all = self.shopinvader_backend.quotation_expose_all
        if show_all:
            # Expose all records bound to current backend or not bound at all.
            backend_domain = [
                "|",
                ("shopinvader_backend_id", "=", self.shopinvader_backend.id),
                ("shopinvader_backend_id", "=", False),
            ]
        return (
            self._default_domain_for_partner_records(with_backend=not show_all)
            + [
                ("typology", "=", "quotation"),
            ]
            + backend_domain
        )

    def _confirm(self, order):
        # If user can see all quotations, bind the order to current backend if not set yet.
        show_all = self.shopinvader_backend.quotation_expose_all
        if show_all and not order.shopinvader_backend_id:
            order = order.with_context(_skip_cart_check=True)
            order.shopinvader_backend_id = self.shopinvader_backend
        return order.action_confirm_cart()
