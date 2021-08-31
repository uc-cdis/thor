# main.py
import os
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from dao.release_dao import readRelease, getRKeys

import logging

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)

app = FastAPI()


@app.get("/releases")
async def read_releases():
    releases_to_return = []    
    keylist = getRKeys()
    for id in keylist:
      r = jsonable_encoder(readRelease(id))
      log.info(f"successfully obtained a release instance from the DAO layer: {r}")
      releases_to_return.append(r)

    return JSONResponse(content={ "releases": releases_to_return })

@app.get("/releases/{release_id}")
async def read_release(release_id):
    r = jsonable_encoder(readRelease(release_id))
    return {"release": r}
