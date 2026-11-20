# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from enum import Enum

from odoo.addons.shopinvader_api_unit_member.schemas import UnitMember as UnitMemberBase


class AuthState(str, Enum):
    none = "none"
    invited = "invited"
    accepted = "accepted"


class UnitMember(UnitMemberBase, extends=True):
    auth_state: AuthState

    @classmethod
    def from_res_partner(cls, odoo_rec):
        res = super().from_res_partner(odoo_rec)
        res.auth_state = odoo_rec.member_auth_state
        return res
