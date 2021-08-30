# main.py

import os
import logging

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from release_dao import readRelease, getRKeys
from task_dao import readTask, getTKeys

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)

app = FastAPI()


@app.get("/releases")
async def getReleases():
    releases_to_return = []
    keylist = getRKeys()
    for id in keylist:
        r = jsonable_encoder(readRelease(id))
        log.info(f"Successfully obtained release instance from DAO layer: {r}")
        releases_to_return.append(r)

    return JSONResponse(content={"releases": releases_to_return})


@app.get("/releases/{release_id}")
async def read_release(release_id):
    r = jsonable_encoder(readRelease(release_id))
    log.info(f"Successfully obtained release info for {release_id}. ")
    return {"release": r}


@app.get("/tasks")
async def getTasks():
    tasks_to_return = []
    keylist = getTKeys()
    for id in keylist:
        r = jsonable_encoder(readTask(id))
        log.info(f"Successfully obtained task instance from DAO layer: {r}")
        tasks_to_return.append(r)

    return JSONResponse(content={"tasks": tasks_to_return})


@app.get("/tasks/{task_id}")
async def read_task(task_id):
    t = jsonable_encoder(readTask(task_id))
    log.info(f"Successfully obtained task info for {task_id}. ")
    return {"task": t}
