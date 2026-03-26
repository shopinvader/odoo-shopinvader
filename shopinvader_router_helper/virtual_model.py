# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from contextlib import contextmanager

from odoo import api, fields, models
from odoo.api import Cache
from odoo.fields import Field

# Add a way to flag virtual fields as virtual
Field._virtual = False


class VirtualModel(models.AbstractModel):
    """
    A virtual model is a model without a database table that you can use
    to hold data in its fields for the lifespan of a request.

    It handles standard odoo fields, relations, computed and related fields.

    It is resilient to cache invalidation.
    """

    _auto = False
    _register = False
    _abstract = True
    _virtual = True

    # This is needed in 18.0 to allow the creation of new abstract records
    # with values (and make relations work):
    id = fields.Id(automatic=True)

    @api.model
    def _setup_base(self):
        rv = super()._setup_base()
        # Flag all virtual models fields as virtual
        for field in self._fields.values():
            field._virtual = True

        return rv


@contextmanager
def _keeping_virtual(self, spec=None):
    """
    Context manager to make virtual fields persistent in cache since
    they are not stored in the database but we want to keep them in case
    of cache invalidation.
    """
    spec_fields = [field for field, _ids in spec] if spec else None
    # Backup virtual fields data
    virtual_data = {
        field: value
        for field, value in self._data.items()
        if (spec_fields is None or field in spec_fields) and field._virtual
    }
    yield
    # Restore virtual fields data
    self._data.update(virtual_data)


# Patch Cache.clear to preserve virtual fields
cache_clear = Cache.clear


def clear(self):
    with _keeping_virtual(self):
        return cache_clear(self)


Cache.clear = clear

# Patch Cache.invalidate to preserve virtual fields
cache_invalidate = Cache.invalidate


def invalidate(self, spec=None):
    with _keeping_virtual(self, spec):
        return cache_invalidate(self, spec)


Cache.invalidate = invalidate
