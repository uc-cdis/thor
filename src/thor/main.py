# main.py

import os
import logging

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from dao.release_dao import readRelease, getRKeys
from dao.task_dao import readTask, getTKeys

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)

app = FastAPI()


@app.get("/releases")
async def getReleases():
    """ Returns all the releases in the Releases table. """
    releases_to_return = []
    keylist = getRKeys()
    for id in keylist:
        r = jsonable_encoder(readRelease(id))
        log.info(f"Successfully obtained release instance from DAO layer: {r}")
        releases_to_return.append(r)

    return JSONResponse(content={"releases": releases_to_return})


@app.get("/releases/{release_id}")
async def read_release(release_id):
    """ Reads out the release associated with a particular release id. """
    r = jsonable_encoder(readRelease(release_id))
    log.info(f"Successfully obtained release info for {release_id}. ")
    return {"release": r}


@app.get("/releases/{release_id}/tasks")
async def get_release_tasks(release_id: int):
    """ This returns all tasks with release_id corresponding to the given input. 
    Currently, it fails without support if release_id is not an int, so this should
    be addressed when appropriate. """
    tasks_to_return = []
    tKeyList = getTKeys()

    for id in tKeyList:
        if readTask(id).get_release_id() == release_id:
            tasks_to_return.append(readTask(id))
    log.info(f"Successfully obtained all tasks info for {release_id}. ")
    return tasks_to_return


@app.get("/releases/{release_id}/tasks/{task_id}")
async def get_release_tasks(release_id: int, task_id: int):
    """ This returns all tasks with release_id corresponding to the given input, and 
    task_id corresponding to the given input. Task_id is theoretically unique for each
    task, so this method is somewhat superfluous, but it's here if needed.  
    Currently, it fails without support if either release_id or task_id are not ints, 
    so this should be addressed when appropriate. """
    tasks_to_return = []
    tKeyList = getTKeys()

    for id in tKeyList:
        if readTask(id).get_release_id() == release_id:
            if id == task_id:
                tasks_to_return.append(readTask(id))
    log.info(f"Successfully obtained task info for {release_id}, {task_id}. ")
    return tasks_to_return


@app.get("/tasks")
async def getTasks():
    """ Returns all the tasks in the Tasks table. """
    tasks_to_return = []
    keylist = getTKeys()
    for id in keylist:
        r = jsonable_encoder(readTask(id))
        log.info(f"Successfully obtained task instance from DAO layer: {r}")
        tasks_to_return.append(r)

    return JSONResponse(content={"tasks": tasks_to_return})


@app.get("/tasks/{task_id}")
async def read_task(task_id):
    """ Reads out the task associated with a given task_id. """
    t = jsonable_encoder(readTask(task_id))
    log.info(f"Successfully obtained task info for {task_id}. ")
    return {"task": t}
