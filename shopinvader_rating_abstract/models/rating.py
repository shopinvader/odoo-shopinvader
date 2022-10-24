# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from contextlib import contextmanager

from odoo import api, fields, models


class Rating(models.Model):
    _inherit = "rating.rating"
    _name = "rating.rating"

    _sql_constraints = [
        ("rating_range", "CHECK(1=1)", "Rating should be between 0 and 5"),
        (
            "rating_range_shopinvader",
            "check(rating >= 1 and rating <= 5)",
            "Rating should be between 1 and 5",
        ),
        (
            "rating_unique",
            "EXCLUDE (res_model WITH =, res_id WITH =, partner_id WITH =)"
            " WHERE (active=True)",
            "You can only rate this resource once",
        ),
    ]

    @api.depends("rating")
    def _compute_rating_str(self):
        for record in self:
            record.rating_str = str(record.rating)

    shopinvader_backend_id = fields.Many2one(
        "shopinvader.backend", string="Backend", required=True
    )
    lang_id = fields.Many2one("res.lang", string="Language", required=True)
    active = fields.Boolean(default=True)
    rating_str = fields.Selection(
        [
            ("0.0", "0"),
            ("1.0", "1"),
            ("2.0", "2"),
            ("3.0", "3"),
            ("4.0", "4"),
            ("5.0", "5"),
        ],
        string="Rating string",
        compute="_compute_rating_str",
        store=True,
        inverse="_inverse_rating_str",
        readonly=True,
    )

    def _inverse_rating_str(self):
        for record in self:
            record.rating = float(record.rating_str)

    def synchronize_rating(self):
        res_model = fields.first(self).res_model
        records = self.env[res_model].browse(self.mapped("res_id"))
        records.synchronize()

    def _send_notification(self, key):
        for record in self:
            model = self.env[record.res_model_id.model]
            subkey = "{key}_{table}".format(key=key, table=model._description)
            record.shopinvader_backend_id._send_notification(subkey, record)

    @contextmanager
    def _write_publisher_comment(self):
        try:

            def _mock_has_group(self_local, group_ext_id):
                return True

            self.env["res.users"]._patch_method("has_group", _mock_has_group)
            yield
        finally:
            self.env["res.users"]._revert_method("has_group")

    def write(self, values):
        if (
            values.get("publisher_comment")
            and self.env.user.has_group("rating_moderation.group_rating_moderation")
            and not self.env.user.has_group("website.group_website_publisher")
        ):
            with self._write_publisher_comment():
                res = super().write(values)

            self._send_notification("rating_publisher_response")
            return res

        return super().write(values)
