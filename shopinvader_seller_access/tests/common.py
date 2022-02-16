from contextlib import contextmanager
from unittest.mock import patch

from ..services import service


class FakeRequest:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class SellerGroupBackendMixin(object):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.backend.seller_access = True
        self.backend.seller_access_group_name = "seller"

    @contextmanager
    def seller_group(self, group="seller"):
        with patch.object(
            service, "request", FakeRequest(jwt_payload={"groups": [group]})
        ):
            yield
