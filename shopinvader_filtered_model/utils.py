# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import typing
from inspect import currentframe
from typing import Generic, TypeVar

from odoo import _, api, models
from odoo.exceptions import MissingError
from odoo.osv import expression

T = TypeVar("T", bound=models.BaseModel)


class FilteredModelAdapter(Generic[T]):
    def __init__(self, env: api.Environment, base_domain: list):
        type_args = typing.get_args(get_orig_class(self))
        if not type_args:
            raise ValueError(
                "You must define the type of the model you want to filter. This "
                "class must be used as a generic class. Example: \n\n"
                "from odoo.addons.base.models.res_partner import Partner\n"
                "adapter = FilteredModelAdapter[ResPartner](env, base_domain)"
            )
        self.env: api.Environment = env
        self._model: T = env[type_args[0]._name]
        self._base_domain: list = base_domain

    def get(self, record_id: int) -> T:
        record = self._model.browse(record_id).filtered_domain(self._base_domain)
        if record:
            return record
        else:
            raise MissingError(_("The record do not exist"))

    def search(self, domain: list) -> T:
        domain = expression.AND([self._base_domain, domain])
        return self._model.search(domain)

    def search_with_count(self, domain: list, limit, offset) -> tuple[int, T]:
        domain = expression.AND([self._base_domain, domain])
        count = self._model.search_count(domain)
        return count, self._model.search(domain, limit=limit, offset=offset)


def get_orig_class(obj):
    """Get original class of an object from within the __init__ method.
    This is a workaround for https://github.com/python/typing/issues/658
    """
    try:
        return object.__getattribute__(obj, "__orig_class__")
    except AttributeError:
        cls = object.__getattribute__(obj, "__class__")

        # Workaround for https://github.com/python/typing/issues/658
        # we search for the first frame where the class is the origin
        # of the method call (the frame where the constructor is called)
        # and we return the object from this frame -> the original class
        frame = currentframe().f_back.f_back
        try:
            while frame:
                try:
                    res = frame.f_locals["self"]
                    if res.__origin__ is cls:
                        return res
                except (KeyError, AttributeError):
                    frame = frame.f_back
        finally:
            del frame

        return cls  # Fallback
