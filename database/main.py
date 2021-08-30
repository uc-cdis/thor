# main.py

import os
import logging

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from release_dao import readRelease, getkeys

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)

app = FastAPI()


@app.get("/releases")
async def getReleases():
    releases_to_return = []
    keylist = getkeys
    for id in keylist:
        r = jsonable_encoder(readRelease(id))
        log.info(f"successfully obtained release instance from DAO layer: {r}")
        releases_to_return.append(r)

    return JSONResponse(content={"releases": releases_to_return})
