# You can build this image locally by running
#   docker build -t epistemix-py .
# You can run `tox` in a container by then running
#   docker run --rm -it epistemix-py

# Image based on 335566905560.dkr.ecr.us-east-1.amazonaws.com/fred-core:latest
# See https://github.com/Epistemix-com/FRED-tools/ for details
FROM --platform=linux/amd64 ubuntu:22.04

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        python3-pip python3-venv

RUN pip install --upgrade pip && \
    pip install --upgrade build twine

CMD sleep infinity
