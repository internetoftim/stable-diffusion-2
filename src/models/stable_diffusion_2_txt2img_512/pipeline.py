# Copyright (c) 2023 Graphcore Ltd. All rights reserved.
from PIL import Image
from diffusers import DPMSolverMultistepScheduler
import os
import logging

logger = logging.getLogger()
    

class SD2Text2ImgModelPipeline:
    def __init__(self):
        import torch
        from optimum.graphcore.diffusers import get_default_ipu_configs, INFERENCE_ENGINES_TO_MODEL_NAMES, IPUStableDiffusionPipeline

        pod_type='pod8'
        engine = 'stable-diffusion-512-v2-1'
        executable_cache_dir = f'./exe_cache/{engine}_{pod_type}/'

        unet_ipu_config, text_encoder_ipu_config, vae_ipu_config, safety_checker_ipu_config = get_default_ipu_configs(
            engine,
            height=512,
            width=512,
            pod_type=pod_type,
            executable_cache_dir=executable_cache_dir
        )

        self._pipe = IPUStableDiffusionPipeline.from_pretrained(
            INFERENCE_ENGINES_TO_MODEL_NAMES[engine],
            revision="fp16",
            torch_dtype=torch.float16,
            unet_ipu_config=unet_ipu_config,
            text_encoder_ipu_config=text_encoder_ipu_config,
            vae_ipu_config=vae_ipu_config,
            safety_checker_ipu_config=safety_checker_ipu_config
        )

        self._pipe.scheduler = DPMSolverMultistepScheduler.from_config(
            self._pipe.scheduler.config
        )

        self._pipe.enable_attention_slicing()

    def __call__(self, inputs):
        import torch

        ret = self._pipe(
            prompt=inputs["prompt"],
            height=512,
            width=512,
            guidance_scale=inputs["guidance_scale"],
            num_inference_steps=inputs["num_inference_steps"],
            generator=torch.manual_seed(inputs["random_seed"])
        )
        
        return {"result": ret["images"]}

pipe = SD2Text2ImgModelPipeline()

def compile(pipe):
    pipe({
        "prompt": "Big red dog",
        "random_seed": 31337,
        "guidance_scale": 9,
        "num_inference_steps": 1,
        }
    )
    return