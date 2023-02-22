FROM quay.io/cdis/python:3.8-buster as builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc g++ musl-dev libffi-dev libgit2-dev libssl-dev make

RUN pip install --upgrade pip poetry

ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

COPY . /src/
WORKDIR /src
RUN python -m venv /env && . /env/bin/activate && poetry install --no-interaction --no-dev

FROM quay.io/cdis/python:3.8-buster

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    postgresql git curl jq

ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1
ENV AWS_REGION=us-west-2
COPY --from=builder /env /env
COPY --from=builder /src /src
ENV PATH="/env/bin/:${PATH}"
WORKDIR /src

CMD ["/env/bin/gunicorn", "thor.main:app", "-b", "0.0.0.0:80", "-k", "uvicorn.workers.UvicornWorker"]