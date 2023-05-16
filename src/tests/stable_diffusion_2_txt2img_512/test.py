# Copyright (c) 2023 Graphcore Ltd. All rights reserved.


def test_stable_diffusion_2_txt2img_512_response(client):
    errors = []
    params = {
        "prompt": "Big red dog",
        "random_seed": 31337,
        "guidance_scale": 9,
        "num_inference_steps": 1,
        }
        
    response = client.post("/stable_diffusion_2_txt2img_512", json=params)
    if response.status_code != 200:
        errors.append(f"HTTP response status code is not {200}")
    if "result" not in response.json().keys():
        errors.append(f"'result' key absent from response")
    if not len(errors) == 0:
        raise Exception(f"TEST FAILED errors:\n{errors}")
