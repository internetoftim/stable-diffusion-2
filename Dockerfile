# Copyright (c) 2023 Graphcore Ltd. All rights reserved.

# set base image (host OS)
FROM graphcore/pytorch:3.2.0-ubuntu-20.04-20230314
WORKDIR .

RUN apt-get -y update
RUN apt-get -y install git

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./src/models/stable_diffusion_2_txt2img_512/requirements.txt stable_diffusion_2_txt2img_512_requirements.txt
RUN pip install -r stable_diffusion_2_txt2img_512_requirements.txt

COPY src ./src
COPY utils ./utils
COPY run_*.sh ./

CMD ./run_server.sh
