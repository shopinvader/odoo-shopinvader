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

    def _get_attribute_value(self, fieldname, one=False, name_key=None):
        if not name_key:
            name_key = self[fieldname]._rec_name
        if one:
            self[fieldname].ensure_one()
            return self[fieldname][name_key]
        else:
            return self[fieldname].mapped(name_key)

    def _get_attr_vals(self, attr, string_mode=False):
        """The value of the attribute as string."""
        self.ensure_one()
        if attr.attribute_type == "select":
            return self._get_attribute_value(attr.name, one=True)
        elif attr.attribute_type == "multiselect":
            return self._get_attribute_value(attr.name)
        elif string_mode and attr.attribute_type == "boolean":
            return self[attr.name] and "true" or "false"
        elif string_mode or attr.attribute_type in ("char", "text"):
            return "%s" % (self[attr.name] or "")
        else:
            return self[attr.name]

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
                        "value": record._get_attr_vals(attr, string_mode=True),
                        # in structured attribute, all value shoud be of
                        # the same type. So we convert it to string
                        "type": attr.attribute_type,
                    }
                )
            record.structured_attributes = list(strc_attr.values())
