# Copyright (c) 2022 Graphcore Ltd. All rights reserved.
import os
import sys

import pytest

from tests.test_server_base import TestServerBase

TESTS_DIRECTORY = os.path.dirname(__file__)
SRC_DIRECTORY = os.path.join(TESTS_DIRECTORY, "..")
sys.path.append(SRC_DIRECTORY)


class TestReplicas(TestServerBase):
    app = None

    @pytest.fixture(autouse=True, scope="module")
    def _prepare(self):
        os.environ["SERVER_MODELS"] = '[{"model":"stable_diffusion_2_txt2img_512","replicas":"2"}]'

    def test_replicas(self, client):
        params = {
        "prompt": "Big red dog",
        "random_seed": 31337,
        "guidance_scale": 9,
        "num_inference_steps": 1,
        }
        
        response = client.post("/stable_diffusion_2_txt2img_512", json=params)
        assert response.status_code == 200
