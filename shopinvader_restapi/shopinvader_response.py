# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import threading

from odoo.http import request

_test_mode = False

threadLocal = threading.local()


class ShopinvaderResponse(object):
    """
    A response object used to enrich the response returned by a shopinvader
    service with cache and session informations
    """

    def __init__(self):
        self._store_cache = {}
        self._session = {}

    def set_store_cache(self, key, value):
        self._store_cache[key] = value

    def set_session(self, key, value):
        self._session[key] = value

    @property
    def store_cache(self):
        """
        Read only store cache values
        :return: dict
        """
        return self._store_cache.copy()

    @property
    def session(self):
        """
        Read only session values
        :return: dict
        """
        return self._session.copy()

    def reset(self):
        """
        Reset the content off the response
        :return:
        """
        self._session = {}
        self._store_cache = {}


def set_testmode(mode):
    global _test_mode
    _test_mode = mode
    if _test_mode:
        get().reset()


def get(raise_if_not_found=True):
    """
    Returns an instance of `ShopinvaderResponse``
    """
    current_local = request
    if _test_mode:
        # in test mode (unittest) request is not available as container to hold
        # our context local data. (in a process/thread safe way). Since we are
        # in test mode we can rely on the threadLocal context
        current_local = threadLocal
    try:
        if not hasattr(current_local, "_shopinvader_response"):
            current_local._shopinvader_response = ShopinvaderResponse()
    except RuntimeError:
        if raise_if_not_found:
            raise
        else:
            return None
    return current_local._shopinvader_response
