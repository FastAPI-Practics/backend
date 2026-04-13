FROM python:3.14.4-slim-bookworm

RUN apt-get update && apt-get install -y openssh-client && \
    apt update -y && \
    apt install rsync -y && \
    python3 -m pip install --user pipx && \
    python3 -m pipx ensurepath && \
    export PATH="${PATH}:$(python3 -c 'import site; print(site.USER_BASE)')/bin" && \
    pipx install --include-deps ansible ansible-lint