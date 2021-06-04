# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ShopinvaderVariant(models.Model):
    _inherit = "shopinvader.variant"

    attributes = fields.Serialized(
        compute="_compute_attributes", string="Shopinvader attributes Fields"
    )
    structured_attributes = fields.Serialized(
        compute="_compute_structured_attributes",
        string="Shopinvader attributes Fields",
    )

    def _get_m2m_name(self, fieldname):
        # It may or may not be a name on the target record
        # TODO: improve it by use an export instead
        try:
            return self[fieldname].mapped("name")
        except KeyError:
            # no "name" on the pointed object
            return [""]

    def _get_attr_vals(self, attr):
        """The raw value of the attribute."""
        self.ensure_one()
        if attr.attribute_type == "select":
            return self._get_m2m_name(attr.name)[0]
        elif attr.attribute_type == "multiselect":
            return self._get_m2m_name(attr.name)
        elif attr.attribute_type in ("char", "text"):
            return "%s" % (self[attr.name] or "")
        return self[attr.name]

    def _get_attr_vals_string(self, attr):
        """The value of the attribute as string."""
        self.ensure_one()
        if attr.attribute_type == "select":
            return self._get_m2m_name(attr.name)[0]
        elif attr.attribute_type == "multiselect":
            return self._get_m2m_name(attr.name)
        elif attr.attribute_type == "boolean":
            return self[attr.name] and "true" or "false"
        else:
            return "%s" % (self[attr.name] or "")

    def _compute_attributes(self):
        for record in self:
            attributes = {}
            for attr in record.attribute_set_id.attribute_ids:
                # all attr start with "x_" we remove it for the export
                attributes[attr.export_name] = record._get_attr_vals(attr)
            record.attributes = attributes

    def _compute_structured_attributes(self):
        for record in self:
            strc_attr = {}
            attr_set = record.attribute_set_id
            groups = attr_set.attribute_ids.mapped("attribute_group_id")
            for group in groups:
                strc_attr[group.id] = {"group_name": group.name, "fields": []}

            for attr in attr_set.attribute_ids:
                strc_attr[attr.attribute_group_id.id]["fields"].append(
                    {
                        "name": attr.field_description,
                        "key": attr.export_name,
                        "value": record._get_attr_vals_string(attr),
                        # in structured attribute, all value shoud be of
                        # the same type. So we convert it to string
                        "type": attr.attribute_type,
                    }
                )
            record.structured_attributes = list(strc_attr.values())
