# Copyright (c) 2022 Graphcore Ltd. All rights reserved.
from fastapi import FastAPI, Response, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from ipu_worker import IPUWorkerGroup
from config import settings
import logging
import importlib


logger = logging.getLogger()

app = FastAPI()
models = settings.server_models

try:
    assert models != []
except Exception as e:
    logger.error("No model specified for environment.")
    raise e

ipu_worker_group = IPUWorkerGroup(model_list=models)

for model_name in models:
    module = importlib.import_module("models." + model_name.get_name() + ".endpoint")
    app.include_router(module.router)


@app.on_event("startup")
def startup_event():
    print("Running the following models:", models)
    ipu_worker_group.start()
    return


@app.on_event("shutdown")
def shutdown_event():
    ipu_worker_group.stop()
    return


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/")
async def home():
    return {"message": "Health Check Passed!"}


# The health checks [readiness] directory according to guidelines from Paperspace:
# https://docs.paperspace.com/gradient/deployments/healthchecks/
@app.get("/readiness/", status_code=status.HTTP_200_OK)
def readiness_check(response: Response):
    message = "Readiness check succeeded."
    if not ipu_worker_group.is_ready():
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        message = "Readiness check failed."
    return {"message": message}



# The readiness health check is meant to inform
# whether the server is ready to receive requests or not
@app.get("/health/readiness/", status_code=status.HTTP_200_OK)
def readiness_check(response: Response):
    message = "Readiness check succeeded."
    if not ipu_worker_group.is_ready():
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        message = "Readiness check failed."
    return {"message": message}


# As soon as we start the server, the endpoints are ready to be read
@app.get("/health/startup/", status_code=status.HTTP_200_OK)
def startup_check():
    return {"message": "Startup check succeeded."}


# The liveness health check is meant to detect unrecoverable errors
# the server needs restart if unhealthy state is detected
@app.get("/health/liveness/", status_code=status.HTTP_200_OK)
def liveness_check(response: Response):
    message = "Liveness check succeeded."
    if not ipu_worker_group.is_alive():
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        message = "Liveness check failed."
    return {"message": message}