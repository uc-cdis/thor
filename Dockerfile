ARG AZLINUX_BASE_VERSION=master

FROM quay.io/cdis/python-nginx-al:${AZLINUX_BASE_VERSION} AS base

# Install vim and findutils (which provides `find`)
RUN dnf install -y vim findutils curl bash && \
    dnf install -y openssl && \
    dnf clean all && \
    rm -rf /var/cache/dnf

# Install yq (v4+ from mikefarah)
RUN curl -L https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -o /usr/local/bin/yq \
    && chmod +x /usr/local/bin/yq


COPY --chown=gen3:gen3 . /src

WORKDIR /src

USER gen3

RUN poetry install --no-interaction --only main

CMD ["poetry", "run", "gunicorn", "-b", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker", "--timeout", "1800", "thor.main:app"]