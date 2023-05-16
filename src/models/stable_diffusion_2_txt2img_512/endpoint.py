# Copyright (c) 2022 Graphcore Ltd. All rights reserved.
import time
import base64
import io

from pydantic import BaseModel
from PIL import Image

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from fastapi.security.api_key import APIKey

from config import settings
from server import ipu_worker_group

models = settings.server_models

class StableDiffusionRequest(BaseModel):
    prompt: str = "Big red dog"
    random_seed: int = int(time.time())
    guidance_scale: float = 7.5
    return_json: bool = False

class StableDiffusion2Request(StableDiffusionRequest):
    negative_prompt: str = None
    guidance_scale: float = 9
    num_inference_steps: int = 25

router = APIRouter(tags=['API_DEPLOYMENT'])

def prepare_image_response(pipeline_output, headers, return_json: bool):
    if return_json:
        images_b64 = []
        for image in pipeline_output["result"]:
            image_binary = io.BytesIO()
            image.save(image_binary, format="PNG")
            image_binary = image_binary.getvalue()
            images_b64.append(base64.b64encode(image_binary))
        return {"images": images_b64}
    else:
        # single image support only for now
        image = pipeline_output["result"][0]
        image_binary = io.BytesIO()
        image.save(image_binary, format="PNG")
        return Response(
            content=image_binary.getvalue(), headers=headers, media_type="image/png"
        )

@router.post(
    "/stable_diffusion_2_txt2img_512",
    include_in_schema="stable_diffusion_2_txt2img_512" in models,
)
def run_stable_diffusion_2_txt2img_512(
    model_input: StableDiffusion2Request
):
    start = time.time()

    data_dict = model_input.dict()
    ipu_worker_group.workers["stable_diffusion_2_txt2img_512"].feed(data_dict)
    result = ipu_worker_group.workers["stable_diffusion_2_txt2img_512"].get_result()

    latency = time.time() - start

    headers = {
        "metrics-worker-latency": str(latency),
        "metrics-model-latency": str(result["model_latency"]),
    }

    return prepare_image_response(result, headers, model_input.return_json)
