FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get -qq update \
    && apt-get -qq install --no-install-recommends --yes \
    git \
    python3 \
    python3-dev \
    python3-pip \
    python3-venv \
    python-is-python3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /output && chmod -R a+rwx /output

RUN python3 -m venv /opt/venv
ENV PATH=/opt/venv/bin:${PATH}

COPY docker/crop/requirements.txt /opt
RUN pip install -r /opt/requirements.txt \
 && rm -rf /root/.cache /opt/requirements.txt

COPY bin /opt

CMD ["/bin/bash"]
