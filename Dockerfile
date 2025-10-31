ARG PYTHON_VERSION=feat_python3.13-alias

FROM quay.io/cdis/python-build-base:${PYTHON_VERSION} AS builder

# Install vim and findutils (which provides `find`)
RUN dnf install -y vim findutils jq && \
    dnf install -y openssl && \
    dnf clean all && \
    rm -rf /var/cache/dnf

RUN chown -R gen3:gen3 /venv

COPY --chown=gen3:gen3 . /src

WORKDIR /src

USER gen3

RUN poetry install --no-interaction --only main

CMD ["poetry", "run", "gunicorn", "-b", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker", "--timeout", "1800", "thor.main:app"]