# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import AbstractComponent


class AbstractMailService(AbstractComponent):
    _inherit = "base.shopinvader.service"
    _name = "shopinvader.abstract.mail.service"

    def ask_email(self, _id):
        """
        Ask to receive the record ID by email
        :param _id: int
        :return:
        """
        self._ask_email(_id)
        return {}

    def _validator_ask_email(self):
        return {}

    def _get_email_notification_type(self, record):
        """
        Based on the given record, get the notification type.
        By default, it's build like this:
        <_usage>_send_email
        :param record: target record
        :return: str
        """
        if hasattr(self, "_usage") and self._usage:
            return "%s_send_email" % self._usage
        return ""

    def _load_target_email(self, record_id):
        """
        Load the record (based on expose model)
        :param record_id: int
        :return: record or None
        """
        if not getattr(self, "_expose_model", False):
            return None
        return self.env[self._expose_model].browse(record_id)

    def _get_email_recipient(self, record, notif_type):
        """
        Get the default recipient of the given record (partner_id by default).
        :param record: target record
        :param notif_type: str
        :return: res.partner recordset
        """
        partner = self.env["res.partner"].browse()
        if record and hasattr(record, "partner_id") and record.partner_id:
            partner = record.partner_id
        return partner

    def _allow_email_notification(self, partner, record, notif_type):
        """
        Based on given record, partner and notif_type, check if the partner
        is allowed to launch this kind of notification
        :param partner: res.partner
        :param record: target record
        :param notif_type: str
        :return: bool
        """
        if not notif_type:
            return False
        recipient_partner = self._get_email_recipient(record, notif_type)
        return partner == recipient_partner

    def _ask_email(self, _id):
        """
        Send the notification about the email on the backend
        :param _id: int
        :return: dict
        """
        # Can not ask an email if not logged
        if not self._is_logged_in():
            return {}
        target = self._load_target_email(_id)
        if not target:
            return {}
        notif_type = self._get_email_notification_type(target)
        allow = self._allow_email_notification(
            self.partner, target, notif_type
        )
        if notif_type and allow:
            self._launch_notification(target, notif_type)
        return {}

    def _launch_notification(self, targets, notif_type):
        """
        Action to launch the notification (on the current backend) for the
        given record
        :param targets: recordset
        :param notif_type: str
        :return: bool
        """
        if not targets:
            return True
        for target in targets:
            self.shopinvader_backend._send_notification(notif_type, target)
        return True
