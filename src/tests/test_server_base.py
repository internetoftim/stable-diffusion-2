# Copyright (c) 2023 Graphcore Ltd. All rights reserved.
import os
import sys
from importlib import reload

from fastapi.testclient import TestClient


class TestServerBase:
    app = None

    @classmethod
    def reload_server(self):
        import config

        reload(config)
        import server

        self.app = reload(server).app

    def setup_class(self):
        print(f"setup_class called for the {self.__name__}")
        self.reload_server()
        self.test_client = TestClient(self.app)
        self.test_client = self.test_client.__enter__()

    def teardown_class(self):
        print(f"teardown_class called for the {self.__name__}")
        self.test_client.__exit__()
