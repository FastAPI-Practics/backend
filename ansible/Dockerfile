FROM python:3.14.4-slim-bookworm AS base
FROM base AS builder

RUN pip install --no-cache-dir ansible==8.7.0

COPY requirements.yml /tmp/requirements.yml
RUN ansible-galaxy collection install -r /tmp/requirements.yml -p /collections

FROM base

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    openssh-client \
    git \
    rsync \
    jq \
    sshpass \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    ansible==8.7.0 \
    jmespath

COPY --from=builder /collections /root/.ansible/collections

WORKDIR /ansible