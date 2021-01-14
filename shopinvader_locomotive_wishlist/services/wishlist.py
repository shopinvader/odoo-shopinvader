# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.component.core import Component


class WishlistService(Component):
    _inherit = "shopinvader.wishlist.service"

    def _replace_items(self, record, params):
        set_lines = super()._replace_items(record, params)
        # `replace_items` uses SQL to avoid useless writes
        # hence the normal write event is not triggered on lines.
        # Trigger forced sync on the wishlist itself.
        record._event("on_record_write").notify(
            record.with_context(_force_export=True)
        )
        return set_lines
