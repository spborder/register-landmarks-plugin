FROM condaforge/mambaforge

RUN mamba install python=3.10
RUN mamba install -c conda-forge gcc libgdal gxx imagecodecs -y

LABEL maintainer="Sam Border - Computational Microscopy Imaging Lab. <samuel.border@medicine.ufl.edu>"

RUN apt-get update && \
    apt-get autoremove && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    wget \
    curl \
    ca-certificates \
    libcurl4-openssl-dev \
    libexpat1-dev \
    unzip \
    libhdf5-dev \
    software-properties-common \
    libssl-dev \
    # Standard build tools \
    build-essential \
    cmake \
    autoconf \
    automake \
    libtool \
    pkg-config \
    libmemcached-dev && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN apt-get update ##[edited]

RUN apt-get install libxml2-dev libxslt1-dev -y

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y

WORKDIR /

ENV build_path=$PWD/build
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

# Copying location of scripts
ENV reg_path=$PWD/register_landmarks_plugin
RUN mkdir -p $reg_path

RUN apt-get update && \
    apt-get install -y --no-install-recommends memcached && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY . $reg_path/
WORKDIR $reg_path

#   Upgrade setuptools, as the version in Conda won't upgrade cleanly unless it
# is ignored.

# Installing packages in setup.py
RUN pip install --no-cache-dir --upgrade --ignore-installed pip setuptools && \
    pip install --no-cache-dir .  --find-links https://girder.github.io/large_image_wheels && \
    rm -rf /root/.cache/pip/*

# Show what was installed
RUN python --version && pip --version && pip freeze

# pregenerate font cache
#RUN python -c "from matplotlib import pylab"

# define entrypoint through which all CLIs can be run
WORKDIR $reg_path/register_landmarks_plugin/cli

# Test our entrypoint.  If we have incompatible versions of numpy and
# openslide, one of these will fail
RUN python -m slicer_cli_web.cli_list_entrypoint --list_cli
RUN python -m slicer_cli_web.cli_list_entrypoint RegisterLandmarks --help


ENTRYPOINT ["/bin/bash", "docker-entrypoint.sh"]












