# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, exceptions, fields, models


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    def _get_default_quotation_reminder_mail_template_id(self):
        """
        Get the default mail template to use for reminder
        :return: mail.template recordset
        """
        xml_id = (
            "shopinvader_pending_cart_reminder."
            "mail_template_shopinvader_sale_reminder"
        )
        mail_template = self.env.ref(xml_id, raise_if_not_found=False)
        if not mail_template:
            mail_template = self.env["mail.template"].browse()
        return mail_template

    pending_cart_reminder_delay = fields.Integer(
        string="Quotation reminder (hours)",
        help="Determine after how many hours the customer should receive a "
        "reminder to confirm his sale. Let 0 (or less) to disable the "
        "feature.",
        default=0,
    )
    pending_cart_reminder_template_id = fields.Many2one(
        comodel_name="mail.template",
        string="Quotation reminder e-mail template",
        domain="[('model_id', '=', 'sale.order')]",
        default=lambda x: x._get_default_quotation_reminder_mail_template_id(),
    )
    reminder_start_date = fields.Date(
        default=fields.Date.today,
        help="Determine the date start to send reminder emails.\n"
        "This field is automatically updated when the Quotation "
        "Reminder field have a value <= 0 (considered as disabled) and "
        "updated to > 0 (considered as enable).",
    )

    def write(self, vals):
        """
        Inherit to auto-fill the reminder_start_date if necessary
        :param vals: dict
        :return: bool
        """
        self_at_zero = self.filtered(lambda r: r.pending_cart_reminder_delay <= 0)
        self_others = self - self_at_zero
        result = True
        if self_at_zero:
            values_at_zero = self_at_zero._fill_reminder_start_date(vals.copy())
            result = super(ShopinvaderBackend, self_at_zero).write(values_at_zero)
        if self_others:
            result = super(ShopinvaderBackend, self_others).write(vals)
        return result

    @api.model
    def _fill_reminder_start_date(self, values):
        """
        Fill the reminder_start_date if the pending_cart_reminder_delay is
        updated to > 0.
        This auto-update is like a onchange. But the onchange could have
        unexpected behavior.
        Example:
        if we have the onchange, and the pending_cart_reminder_delay set to 0
        (so reminder is disable).
        Then the user enable it (pending_cart_reminder_delay = 10).
        So the onchange fill the reminder_start_date with today.
        Few days later, the user change the pending_cart_reminder_delay to 0
        to disable the reminder (without clicking on save button).
        But finally, the user
        re-change the pending_cart_reminder_delay to 5.
        So the onchange is triggered
        and the reminder_start_date will be set to today (and now the user
        click on save). So every SO created recently could not received
        reminder emails.
        @pre: The self should be only records where the current value of
        pending_cart_reminder_delay is 0 (or less).
        :param values: dict
        :return: dict
        """
        if values.get("pending_cart_reminder_delay", 0) > 0:
            values.update({"reminder_start_date": fields.Date.today()})
        return values

    @api.constrains("pending_cart_reminder_template_id", "pending_cart_reminder_delay")
    def _constrains_quotation_reminder(self):
        """
        Constrain function to ensure that the email template is filled
        if the quotation reminder is > 0
        :return:
        """
        bad_records = self.filtered(
            lambda r: r.pending_cart_reminder_delay > 0
            and not r.pending_cart_reminder_template_id
        )
        if bad_records:
            details = "\n- ".join(bad_records.mapped("display_name"))
            message = (
                _(
                    "Please define an email template to send reminder for "
                    "these backends:\n- %s"
                )
                % details
            )
            raise exceptions.ValidationError(message)
