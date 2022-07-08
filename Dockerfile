FROM ubuntu:22.04 AS builder
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y curl \
                          g++-9 \
                          git \
                          make \
                          ninja-build \
                          python3-pip \
                          python3.10-venv # For generating pip package.

# Download and install CMake
ARG CMAKE_VERSION="3.22.2"
ARG CMAKE_ARCH="linux-x86_64"
ARG CMAKE_FILENAME="cmake-$CMAKE_VERSION-$CMAKE_ARCH"
ARG CMAKE_URL_TARGET="https://github.com/Kitware/CMake/releases/download/v$CMAKE_VERSION/$CMAKE_FILENAME.tar.gz"
RUN curl -L $CMAKE_URL_TARGET -o /tmp/$CMAKE_FILENAME.tar.gz \
    && tar -zxf /tmp/$CMAKE_FILENAME.tar.gz --directory /opt \
    && ln -s /opt/$CMAKE_FILENAME/bin/cmake /bin/cmake

ARG GITHUB_ACCESS_TOKEN
ARG TAG=dev

# Clone and build FRED-dev repo
RUN git clone --depth 1 --branch ${TAG} \
    https://${GITHUB_ACCESS_TOKEN}@github.com/Epistemix-com/FRED-dev.git /tmp/FRED-dev \
    && cd /tmp/FRED-dev \
    && make release

RUN git clone --depth 1 https://${GITHUB_ACCESS_TOKEN}@github.com/Epistemix-com/Quickstart-Guide.git /tmp/Quickstart-Guide \
    && rm -rf /tmp/Quickstart-Guide/.git

# You can build this image locally by running
#   docker build -t epistemix-py .
# You can run `tox` in a container by then running
#   docker run --rm -it epistemix-py

# Image based on 335566905560.dkr.ecr.us-east-1.amazonaws.com/fred-core:latest
# See https://github.com/Epistemix-com/FRED-tools/ for details
FROM --platform=linux/amd64 ubuntu:22.04

RUN apt-get update && apt-get install -y git python3-pip

RUN pip install --upgrade pip && \
    pip install --upgrade build twine

ARG FRED_HOME=/opt/FRED
ENV FRED_HOME=${FRED_HOME}
ENV FRED_AUTH_KEY=${FRED_HOME}/FRED_AUTH_KEY
ENV FRED_DATA=${FRED_HOME}/data
ENV FRED_PATH=${FRED_HOME}
ENV FRED_PROJECT=${FRED_HOME}/project
ENV FRED_RESULTS=${FRED_HOME}/results

RUN mkdir -p ${FRED_HOME}/data \
    && mkdir -p ${FRED_HOME}/project \
    && mkdir -p ${FRED_HOME}/results

# RUN curl -o /fred-data.tar.gz https://synthetic-population-epistemix-usa-2010v4-all.s3.amazonaws.com/FRED-data.tar.gz \
#     && tar -xvf /fred-data.tar.gz --directory $FRED_HOME/data \
#     && rm /fred-data.tar.gz
COPY --from=builder /tmp/FRED-dev/library ${FRED_HOME}/library
COPY --from=builder /tmp/FRED-dev/bin ${FRED_HOME}/bin
COPY --from=builder /tmp/FRED-dev/FRED_AUTH_KEY ${FRED_HOME}/FRED_AUTH_KEY
COPY --from=builder /tmp/FRED-dev/data ${FRED_HOME}/data

ENV PATH="$PATH:/opt/FRED/bin"

COPY --from=builder /tmp/Quickstart-Guide/ /tmp/Quickstart-Guide
RUN chmod --recursive g+rwx,u+rwx /tmp/Quickstart-Guide

CMD sleep infinity
