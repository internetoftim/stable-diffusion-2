# Copyright (c) 2022 Graphcore Ltd. All rights reserved.
import time

import pytest

from tests.test_server_base import TestServerBase


class Timer:
    def __init__(self):
        self.time = 0

    def __enter__(self):
        self.time = time.time()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.time = time.time() - self.time
        if hasattr(self, "q"):
            self.q.append(self.time)

    def set_buffer(self, q):
        self.q = q


class TestApi(TestServerBase):
    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_readiness(client):
        response = client.get("/readiness")
        assert response.status_code == 200
