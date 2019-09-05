import threading

from odoo.http import request

_test_mode = False

threadLocal = threading.local()


def set_testmode(mode):
    global _test_mode
    _test_mode = mode
    if _test_mode:
        get().clear()


def get():
    """
    Returns a mutable dictionary which is injected in service responses.

    Keys supported by the locomotive frontend include:
    - store_cache
    - set_session
    :return:
    """
    current_local = request
    if _test_mode:
        # in test mode (unittest) request is not available as container to hold
        # our context local data. (in a process/thread safe way). Since we are
        # in test mode we can rely on the threadLocal context
        current_local = threadLocal
    if not hasattr(current_local, "_shopinvader_session_data"):
        setattr(current_local, "_shopinvader_session_data", {})
    return current_local._shopinvader_session_data
