# Copyright (c) 2022 Graphcore Ltd. All rights reserved.
from pydantic import BaseSettings, BaseModel
from typing import List

DEFAULT_REPLICA_NUMBER: int = 1


class ModelConfig(BaseModel):
    model: str
    replicas: int = DEFAULT_REPLICA_NUMBER

    def __eq__(self, other):
        if isinstance(other, str):
            return self.model == other
        return (self.x, self.y) == (other.x, other.y)

    def get_name(self):
        return self.model


class Settings(BaseSettings):
    server_models: List[ModelConfig] = [
        {"model": "stable_diffusion_2_txt2img_512"}
    ]

    class Config:
        env_file = "../.env"


settings = Settings()
