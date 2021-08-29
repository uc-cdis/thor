# main.py
import os
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from dao.release_dao import readRelease, getkeys

import logging

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)

app = FastAPI()


@app.get("/releases")
async def getall():
    releases_to_return = []    
    keylist = getkeys()
    for id in keylist:
      r = jsonable_encoder(readRelease(id))
      log.info(f"successfully obtained a release instance from the DAO layer: {r}")
      releases_to_return.append(r)

    return JSONResponse(content={ "releases": releases_to_return })


