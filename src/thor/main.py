# main.py

import os
import logging
import datetime
import json
from platform import release
from turtle import update

from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from thor.dao.release_dao import \
    create_release, read_release, read_all_releases, get_release_keys, \
        update_release, delete_releases, release_id_lookup_class
from thor.dao.task_dao import \
    create_task, read_task, read_all_tasks, get_task_keys, get_release_tasks, \
        update_task, delete_task
from thor.maestro.run_bash_script import attempt_to_run
from thor.time.scheduler import Scheduler
import thor.dao.clear_tables_reseed as ctrs

# Sample POST request with curl:
# curl -X POST --header "Content-Type: application/json" --data @json_objs/sample_task_0.json 0.0.0.0:6565/tasks


class Task(BaseModel):
    task_name: str
    release_id: int
    step_num: int

class TaskStatus(BaseModel):
    status: str


logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)

app = FastAPI(title="Thor Gen3 Release Orchestrator",)


@app.get("/releases")
async def get_all_releases():
    """ Returns all the releases in the Releases table. """

    all_releases = [jsonable_encoder(release) for release in read_all_releases()]
    log.info("Successfully retrieved all releases from Releases. ")
    return JSONResponse(content={"releases": all_releases})


@app.get("/releases/{release_name}")
async def get_single_release(release_name: str):
    """ Reads out the release associated with a particular release name. """
    rid_lookupper = release_id_lookup_class()
    release_id = rid_lookupper.release_id_lookup(release_name)
    release = jsonable_encoder(read_release(release_id))
    log.info(f"Successfully obtained release info for {release_id}. ")
    return JSONResponse(content={"release": release})

@app.post("/releases/{release_name}")
async def create_new_release(release_name: str):
    """ This endpoint is used to create a new release and all associated tasks with status PENDING. """
    release_id = create_release(version = release_name, result = "PENDING")
    log.info(f"Successfully created release with id {release_id}.")
    with open("thor_config.json") as f:
        steps_dict = json.load(f)

    for step in steps_dict:
        task_id = create_task(steps_dict[step]["job_name"], "PENDING", release_id, steps_dict[step]["step_num"])
        log.info(f"Successfully created task with id {task_id} for release with id {release_id}.")
    log.info(f"Successfully created all tasks for release with id {release_id}.")
    return JSONResponse(content={"release_id": release_id})

@app.get("/releases/{release_id}/tasks")
async def get_all_release_tasks(release_id: int):
    """ 
    This returns JSON of all tasks with release_id corresponding to the given input. 
    If there are no such tasks, returns an empty list. 
    """
    tasks_to_return = get_release_tasks(release_id)
    log.info(f"Successfully obtained all tasks info for {release_id}. ")

    all_tasks = [jsonable_encoder(task) for task in tasks_to_return]
    return JSONResponse(content={"release_tasks": all_tasks})


@app.get("/releases/{release_id}/tasks/{task_id}")
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

    all_tasks = [jsonable_encoder(task) for task in tasks_to_return]
    return JSONResponse(content={"release_task": all_tasks})


@app.get("/tasks")
async def get_all_tasks():
    """ Returns all the tasks in the Tasks table. """

    tasks_to_return = [jsonable_encoder(task) for task in read_all_tasks()]
    log.info("Successfully retrieved all tasks from Tasks. ")

    return JSONResponse(content={"tasks": tasks_to_return})

@app.post("/tasks")
async def create_new_task(new_task: Task):
    """ This endpoint is used to create a new task. """
    # First, must check that the release_id is valid.
    release_keys = get_release_keys()
    if new_task.release_id not in release_keys:
        log.error(f"Attempt to create task with invalid release_id {new_task.release_id}.")
        raise HTTPException(status_code=422, detail= \
            [{"loc":["body","release_id"],"msg":"No such release_id exists."}])
    task_id = create_task(name = new_task.task_name, status = "PENDING", \
        release_id = new_task.release_id, step_num = new_task.step_num)
    log.info(f"Successfully created task with id {task_id}.")
    return JSONResponse(content={"task_id": task_id})

@app.put("/tasks/{task_id}")
async def update_task_status(task_id: int, status_obj: TaskStatus):
    """
    This endpoint is used to update the status of a task.
    """
    new_status = status_obj.status
    update_task(task_id, "status", new_status)
    log.info(f"Successfully updated task with id {task_id}.")
    return JSONResponse(content={"task_id": task_id, "status": new_status})

@app.get("/tasks/{task_id}")
async def get_single_task(task_id):
    """ Reads out the task associated with a given task_id. """
    t = jsonable_encoder(read_task(task_id))
    log.info(f"Successfully obtained task info for {task_id}. ")
    return JSONResponse(content={"task": t})


@app.get("/time/test")
async def what_time_is_it():
    """ auxiliary api endpoint to return the current timestamp in which Thor is operating. """
    return {"current_time": datetime.datetime.now()}

@app.post("/releases/{release_id}/start")
async def start_release(release_id: int):
    """
    This endpoint starts a release from the very beginning. 
    Assumes that all tasks thus far have status 'PENDING', 
    and that the release_id is valid. 
    """
    if release_id not in get_release_keys():
        log.error(f"Attempt to start release with invalid release_id {release_id}.")
        raise HTTPException(status_code=422, detail= \
            [{"loc":["body","release_id"],"msg":"No such release_id exists."}])
    update_release(release_id, "result", "In Progress")
    log.info(f"Successfully started release with id {release_id}.")

    # First, we have to find all tasks for this release. 
    release_tasks = get_release_tasks(release_id)
    # Sorting so we can index by step_num. 
    # Assuming that step_num is unique and consecutive. 
    release_tasks.sort(key=lambda x: x.step_num)
    # TODO: Should we insert checking to make sure steps are actually like this?

    # Now, we can execute the tasks in order. 
    # Success logging for return: 
    task_results = {step_num: "PENDING" for step_num in range(1, len(release_tasks)+1)}

    for step in release_tasks:
        update_task(step.task_id, "status", "RUNNING")
        log.info(f"Successfully started task #{step.step_num} with id {step.task_id}.")
        status_code = attempt_to_run(step.step_num)
        if status_code == 0:
            update_task(step.task_id, "status", "SUCCESS")
            log.info(f"Task #{step.step_num} of release {release_id} SUCCESS.")
            task_results[step.step_num] = "SUCCESS"
        else:
            update_task(step.task_id, "status", "FAILED")
            log.info(f"Task #{step.step_num} of release {release_id} FAILED with code {status_code}.")
            task_results[step.step_num] = "FAILED"
            break
    # Now, we can update the release status.
    if all(task_results.values()) == "SUCCESS":
        update_release(release_id, "result", "Success.")
        log.info(f"Successfully completed release {release_id}.")
    else:
        update_release(release_id, "result", "Failed.")
        # fail_index = [task.step_num for task in release_tasks if task.status == "FAILED"][0]
        fail_index = 1
        log.info(f"Failed to complete release {release_id} on task #{fail_index}.")

    return JSONResponse(content={"release_id": release_id, "task_results": task_results})


@app.put("/restart")
async def restart_release(release_id: int):
    """
    Restarts a release from the first unsuccessful step. 
    Will then run through the steps in order until complete or unsuccessful. 
    """
    if release_id not in get_release_keys():
        log.error(f"Attempt to restart release with invalid release_id {release_id}.")
        raise HTTPException(status_code=422, detail= \
            [{"loc":["body","release_id"],"msg":"No such release_id exists."}])
    update_release(release_id, "result", "In Progress")
    log.info(f"Restarted release with id {release_id}.")

    # NOTE: The same caveats as above apply here. 
    release_tasks = get_release_tasks(release_id)
    release_tasks.sort(key=lambda x: x.step_num)  

    task_results = {}
    for step in release_tasks:
        if step.status == "SUCCESS":
            task_results[step.step_num] = "SUCCESS"
        else:
            update_task(step.task_id, "status", "RUNNING")
            log.info(f"Successfully started task with id {step.task_id}.")
            status_code = attempt_to_run(step.step_num)
            if status_code == 0:
                update_task(step.task_id, "status", "SUCCESS")
                log.info(f"Task #{step.step_num} of release {release_id} SUCCESS.")
                task_results[step.step_num] = "SUCCESS"
            else:
                update_task(step.task_id, "status", "FAILED")
                log.info(f"Task #{step.step_num} of release {release_id} FAILED with code {status_code}.")
                task_results[step.step_num] = "FAILED"
                break
    
    print(task_results, set(task_results.values()) == {"SUCCESS"})

    if set(task_results.values()) == {"SUCCESS"}:
        update_release(release_id, "result", "Success.")
        log.info(f"Successfully completed release {release_id}.")
    else:
        update_release(release_id, "result", "Failed.")
        fail_index = next(i for i, x in enumerate(task_results.values()) if x == "FAILED")
        log.info(f"Failed to complete release {release_id} on task #{fail_index}.")
    
    return JSONResponse(content={\
        "release_id": release_id, "status":set(task_results.values()) == {"SUCCESS"}, "task_results": task_results})


@app.put("/run_task/{task_id}")
async def run_task(task_id: int):
    """ This endpoint is used to run a task. """
    task = read_task(task_id)

    if task.status != "PENDING":
        log.error(f"Attempt to run task with status {task.status}.")
        raise HTTPException(status_code=422, detail= \
            [{"loc":["body","status"],"msg":"Task status is not PENDING."}])
    
    update_task(task_id, "status", "RUNNING")
    log.info(f"Successfully set task with id {task_id} to status RUNNING.")
    status_code = attempt_to_run(task.step_num)
    if status_code == 0:
        update_task(task_id, "status", "SUCCESS")
        log.info(f"Task with id {task_id} SUCCESS.")
    else:
        update_task(task_id, "status", "FAILED")
        log.info(f"Task with id {task_id} FAILED with code {status_code}.")
    return JSONResponse(content={"task_id": task_id})


@app.put("/clear")
async def clear_all():
    """ This endpoint is used to clear all data. """
    # Tasks first: 
    task_list = get_task_keys()
    delete_task(task_list)

    # Releases next:
    release_list = get_release_keys()
    delete_releases(release_list)
    # Yeah, the inconsistency here is annoying. 

    log.info("Successfully cleared all data.")
    return JSONResponse(content={"status": "Success."})

@app.put("/reseed")
async def reseed():
    """ Reseeds data using the native reseed() and test data. """
    ctrs.reseed()
    log.info("Successfully reseeded data.")
    return JSONResponse(content={"status": "Success."})
