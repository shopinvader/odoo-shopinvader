# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class SEOTitleMixin(models.AbstractModel):
    """
    Abstract model used to define the seo_title and manual_seo_title fields.
    """

    _name = "seo.title.mixin"
    _description = "SEO Title Mixin"

    seo_title = fields.Char(
        string="SEO Title",
        compute="_compute_seo_title",
        inverse="_inverse_seo_title",
        help="If you specify a custom value and you want to rollback to the "
        "default value, just let the field blank.",
    )
    manual_seo_title = fields.Char(string="Manual SEO Title")

    def _build_seo_title(self):
        """
        Build the SEO Title of the current recordset.
        :return: str
        """
        self.ensure_one()
        return self.display_name

    def _inverse_seo_title(self):
        """
        When the seo_title is updated manually, we have to save it into
        the manual_seo_title.
        :return:
        """
        for record in self:
            record.manual_seo_title = record.seo_title

    @api.depends("manual_seo_title")
    def _compute_seo_title(self):
        """
        Compute the value of the seo_title field
        :return:
        """
        for record in self:
            title = record.manual_seo_title or record._build_seo_title()
            record.seo_title = title
