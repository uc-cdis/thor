# main.py

import os
import logging

from fastapi import FastAPI, APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from thor.dao.release_dao import read_release, get_release_keys
from thor.dao.task_dao import read_task, get_task_keys

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)

router = APIRouter()


def get_app():
    app = FastAPI(title="Thor Gen3 Release Orchestrator",)
    app.include_router(router)

    @app.on_event("startup")
    async def startup_event():
        print("scheduler should be initialized here...")

    return app


@router.get("/releases")
async def get_all_releases():
    """ Returns all the releases in the Releases table. """
    releases_to_return = []
    key_list = get_release_keys()
    for key in key_list:
        release = jsonable_encoder(read_release(key))
        log.info(f"Successfully obtained release instance from DAO layer: {release}")
        releases_to_return.append(release)

    return JSONResponse(content={"releases": releases_to_return})


@router.get("/releases/{release_id}")
async def get_single_release(release_id):
    """ Reads out the release associated with a particular release_id. """
    release = jsonable_encoder(read_release(release_id))
    log.info(f"Successfully obtained release info for {release_id}. ")
    return {"release": release}


@router.get("/releases/{release_id}/tasks")
async def get_all_release_tasks(release_id: int):
    """ This returns all tasks with release_id corresponding to the given input. 
    Currently, it fails without support if release_id is not an int, so this should
    be addressed when appropriate. """
    tasks_to_return = []
    tKeyList = get_task_keys()

    for id in tKeyList:
        if read_task(id).get_release_id() == release_id:
            tasks_to_return.append(read_task(id))
    log.info(f"Successfully obtained all tasks info for {release_id}. ")
    return tasks_to_return


@router.get("/releases/{release_id}/tasks/{task_id}")
async def get_release_task_specific(release_id: int, task_id: int):
    """ This returns all tasks with release_id corresponding to the given input, and 
    task_id corresponding to the given input. Task_id is theoretically unique for each
    task, so this method is somewhat superfluous, but it's here if needed.  
    Currently, it fails without support if either release_id or task_id are not ints, 
    so this should be addressed when appropriate. """
    tasks_to_return = []
    task_key_list = get_task_keys()

    for key in task_key_list:
        if read_task(key).get_release_id() == release_id:
            if key == task_id:
                tasks_to_return.append(read_task(key))
    log.info(f"Successfully obtained task info for {release_id}, {task_id}. ")
    return tasks_to_return


@router.get("/tasks")
async def get_all_tasks():
    """ Returns all the tasks in the Tasks table. """
    tasks_to_return = []
    key_list = get_task_keys()
    for key in key_list:
        release = jsonable_encoder(read_task(key))
        log.info(f"Successfully obtained task instance from DAO layer: {release}")
        tasks_to_return.append(release)

    return JSONResponse(content={"tasks": tasks_to_return})


@router.get("/tasks/{task_id}")
async def get_single_task(task_id):
    """ Reads out the task associated with a given task_id. """
    t = jsonable_encoder(read_task(task_id))
    log.info(f"Successfully obtained task info for {task_id}. ")
    return {"task": t}
