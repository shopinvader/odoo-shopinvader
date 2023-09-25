# Copyright 2023 KMEE INFORMATICA LTDA (http://www.kmee.com.br).
# @author Cristiano Rodrigues <cristiano.rodrigues@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class SearchServiceCitiesShopinvader(Component):
    """Expose Search Cities across the state service under /shopinvader endpoint"""

    _name = "search.service.cities.shopinvader"
    _inherit = ["search.service.cities", "base.shopinvader.service"]
    _usage = "city"
    _collection = "shopinvader.backend"
