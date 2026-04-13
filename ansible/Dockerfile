FROM python:3.14.4-slim-bookworm

RUN pip install --no-cache-dir ansible==8.7.0

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    openssh-client \
    git \
    rsync \
    jq \
    sshpass \
    && rm -rf /var/lib/apt/lists/*