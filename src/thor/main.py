# main.py

import os
import logging
import datetime
import json

import requests
# from platform import release
# from turtle import update

from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from thor.dao.release_dao import \
    create_release, read_release, read_all_releases, get_release_keys, \
        update_release, delete_releases, release_id_lookup_class
from thor.dao.task_dao import \
    create_task, read_task, read_all_tasks, get_task_keys, get_release_tasks, get_release_task_step,\
        update_task, delete_task
import thor.dao.clear_tables_reseed as ctrs
from thor.maestro.bash import BashJobManager

# Sample POST request with curl:
# curl -X POST --header "Content-Type: application/json" --data @json_objs/sample_task_0.json 0.0.0.0:6565/tasks

DEVELOPMENT = os.getenv("DEVELOPMENT")


class Task(BaseModel):
    task_name: str
    release_id: int
    step_num: int

class TaskStatus(BaseModel):
    status: str

class TaskIdentifier(BaseModel):
    release_name: str
    step_num: int

def post_slack(text):
    if DEVELOPMENT!="true":
        slack_hook = os.getenv("SLACK_WEBHOOK")
        try:
            requests.post(url=slack_hook, json={"text":text})
        except Exception as e:
            raise e


logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)

app = FastAPI(title="Thor Gen3 Release Orchestrator",)

@app.get("/", response_class=HTMLResponse)
async def index():
    ''' Home page '''
    return """
    <html>
        <head>
            <title>Welcome to Thor!</title>
        </head>
        <body>
            <h3>To get information on all releases, click on <a href="/releases">releases</a></h3>
        </body>
    </html>
    """ 


@app.get("/status", response_class=HTMLResponse)
async def status_response():
    ''' Basic Status UI page '''
    with open("src/thor/status_ui.html") as status_html:
        html_table = status_html.read()

    return html_table


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


@app.post("/thor-admin/releases/{release_name}")
async def create_new_release(release_name: str):
    """ This endpoint is used to create a new release and all associated tasks with status PENDING. """
    release_id = create_release(version = release_name, result = "PENDING")
    log.info(f"Successfully created release with id {release_id}.")

    if DEVELOPMENT == "true":
        with open("dummy_thor_config.json") as f:
            steps_dict = json.load(f)
    else:
        with open("thor_config.json") as f:
            steps_dict = json.load(f)

    for step in steps_dict:
        task_id = create_task(steps_dict[step]["job_description"], "PENDING", release_id, steps_dict[step]["step_num"])
        log.info(f"Successfully created task with id {task_id} for release with id {release_id}.")
    log.info(f"Successfully created all tasks for release with id {release_id}.")
    return JSONResponse(content={"release_id": release_id})


@app.get("/releases/{release_name}/tasks")
async def get_all_release_tasks(release_name: str):
    """ 
    This returns JSON of all tasks with release_name corresponding to the given name. 
    If there are no such tasks, returns an empty list. 
    """
    rid_lookupper = release_id_lookup_class()
    release_id = rid_lookupper.release_id_lookup(release_name)
    tasks_to_return = get_release_tasks(release_id)
    log.info(f"Successfully obtained all tasks info for {release_id}. ")

    all_tasks = [jsonable_encoder(task) for task in tasks_to_return]
    return JSONResponse(content={"release_tasks": all_tasks})


@app.get("/releases/{release_name}/tasks/{step_num}")
async def get_release_task_specific(release_name: str, step_num: int):
    """ This returns the task with release_name corresponding to the given input, and 
    step_num corresponding to the given input. There should only be one such task. 
    If there are no such tasks, returns a JSON with task:None. """

    task_to_return = get_release_task_step(release_name, step_num)

    if task_to_return is None:
        log.info(f"No task found for release with name {release_name} and step_num {step_num}.")
        raise HTTPException(status_code=404, detail=f"No task found for release with name {release_name} and step_num {step_num}.")
    else:
        task = jsonable_encoder(task_to_return)
        log.info(f"Successfully obtained task info for release with name {release_name} and step_num {step_num}.")
        return JSONResponse(content={"task": task})


@app.get("/tasks")
async def get_all_tasks(release_name: str = None, step_num: int = None):
    # Due to change in spec, we also support passing release_name and step_num
    # as query parameters to select a single task, or passing release_name only
    # to select all tasks for a release.
    """ 
    Takes in a release_name and step_num as query parameters, 
    and returns the corresponding task with the given release_name and step_num.
    If only release_name is given, returns all tasks for that release.
    If no query parameters passed, returns all the tasks in the Tasks table. 
    """

    if release_name and step_num:
        return await get_release_task_specific(release_name, step_num)
    elif release_name == None and step_num == None:
        tasks_to_return = [jsonable_encoder(task) for task in read_all_tasks()]
        log.info("Successfully retrieved all tasks from Tasks. ")
        return JSONResponse(content={"tasks": tasks_to_return})
    else:
        if release_name:
            return await get_all_release_tasks(release_name)
        if step_num:
            raise HTTPException(status_code=400, detail="Please provide release_name in addition to step_num.")


@app.post("/thor-admin/tasks")
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


@app.put("/thor-admin/releases/{release_name}/tasks/{step_num}")
async def update_task_status(release_name: str, step_num: int, status_obj: TaskStatus):
    """
    This endpoint is used to update the status of a task.
    """
    new_status = status_obj.status
    task_to_update = get_release_task_step(release_name, step_num)
    if task_to_update is None:
        log.error(f"Attempt to update task with invalid release_name {release_name} and step_num {step_num}.")
        raise HTTPException(status_code=422, detail= \
            [{"loc":["body","release_name"],"msg":f"No task with step_num {step_num} and release_name {release_name} exists."}])
    else:
        try:
            update_task(task_to_update.task_id, "status", new_status)
            log.info(f"Successfully updated task for step {step_num} for release {release_name}.")
            return JSONResponse(content={
                "release_name": release_name, 
                "step_num": step_num,
                "status": new_status
                })
        except Exception as e:
            log.info(f"Exception when updating task {release_name}:{step_num}:")
            log.info(f"{e}")
            raise HTTPException(status_code=422, detail= \
            [{"loc":["body","status"],"msg":f"\"{new_status}\" is not a valid status. "}])


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


@app.post("/thor-admin/releases/{release_name}/start")
async def start_release(release_name: str):
    """
    This endpoint starts a release from the very beginning. 
    Creates the release from scratch and starts from the first step. 
    Checks that the release doesn't already exist. 
    """
    rid_lookupper = release_id_lookup_class()
    release_id = rid_lookupper.release_id_lookup(release_name)

    if release_id != None: # If not none, then it already exists - this should be avoided.
        log.error(f"Attempt to start release with name {release_name} that already exists.")
        raise HTTPException(status_code=422, detail= \
            [{"loc":["body","release_name"],"msg":f"Release with name {release_name} already exists."}])
    else:
        create_release_results = await create_new_release(release_name)
        release_id = json.loads(create_release_results.body.decode("utf-8"))["release_id"]
        log.info(f"Successfully created release with name {release_name} and id {release_id}.")    

    update_release(release_id, "result", "RUNNING")
    os.environ["RELEASE_VERSION"] = release_name
    log.info(f"Successfully started release with name {release_name}.")

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
        step_body = TaskIdentifier(release_name=release_name, step_num=step.step_num)
        step_results = await start_task(task_identifier = step_body)
        step_status = json.loads(step_results.body.decode("utf-8"))["status"]
        task_results[step.step_num] = step_status
        
        if step_status != "SUCCESS": 
            # This is expected to only be "FAILED", but if we expand in the future,
            # some logic will have to be reworked below. 
            break

    # Release status updating is mostly being handled by thor-admin/task/start

    if set(task_results.values()) != {"SUCCESS"}:
        fail_index = [k for (k, v) in task_results.items() if v == "FAILED"]
        log.info(f"Started release {release_name} but failed on task #{fail_index}.")

    return JSONResponse(content={"release_name": release_name, "task_results": task_results,\
        "status": "RELEASED" if set(task_results.values()) == {"SUCCESS"} else "PAUSED"})


@app.post("/thor-admin/releases/{release_name}/restart")
async def restart_release(release_name: str):
    """
    Restarts a release from the first unsuccessful step. 
    Will then run through the steps in order until complete or unsuccessful. 
    """
    rid_lookupper = release_id_lookup_class()
    release_id = rid_lookupper.release_id_lookup(release_name)

    if release_id not in get_release_keys():
        log.error(f"Attempt to restart release with invalid name {release_name}.")
        raise HTTPException(status_code=422, detail= \
            [{"loc":["body","release_name"],"msg":f"No release with name {release_name} exists."}])
    update_release(release_id, "result", "RUNNING")
    os.environ["RELEASE_VERSION"] = release_name
    log.info(f"Restarted release with name {release_name}.")

    # NOTE: The same caveats as above apply here. 
    release_tasks = get_release_tasks(release_id)
    release_tasks.sort(key=lambda x: x.step_num)  

    task_results = {}
    for step in release_tasks:
        if str(step.status) == "SUCCESS":
            task_results[step.step_num] = "SUCCESS"
        else:
            step_body = TaskIdentifier(release_name=release_name, step_num=step.step_num)
            step_results = await start_task(task_identifier = step_body)
            step_status = json.loads(step_results.body.decode("utf-8"))["status"]
            if step_status == "SUCCESS":
                task_results[step.step_num] = "SUCCESS"
            # Some more support for different statuses might be nice, 
            # but that depends on how smart we want thor to be at restarting tasks.
            else:
                task_results[step.step_num] = "FAILED"
                break

    # Same note about /task/start as above applies here wrt release status

    if set(task_results.values()) != {"SUCCESS"}:
        fail_index = next(i for i, x in enumerate(task_results.values()) if x == "FAILED")
        log.info(f"Restart of release {release_name} failed on task #{fail_index}.")
    
    return JSONResponse(content={\
        "release_name": release_name, "task_results": task_results, \
            "status": "RELEASED" if set(task_results.values()) == {"SUCCESS"} else "PAUSED"})


@app.post("/thor-admin/tasks/start")
async def start_task(task_identifier: TaskIdentifier):
    """ This endpoint is used to run a specific step in a release. """
    # Identifying task
    release_name = task_identifier.release_name
    step_num = task_identifier.step_num
    release_name_list = [r.version for r in read_all_releases()]
    if release_name not in release_name_list:
        log.error(f"Attempt to start task with invalid release name {release_name}.")
        raise HTTPException(status_code=422, detail= \
            [{"loc":["body","release_name"],"msg":f"Release_name {release_name} does not exist."}])
    
    current_task = get_release_task_step(release_name, step_num)
    
    if current_task == None:
        log.error(f"Attempt to start task with invalid step number {step_num}.")
        raise HTTPException(status_code=422, detail= \
            [{"loc":["body","step_num"],"msg":f"No step with number {step_num} exists."}])

    task_id = current_task.task_id
    release_id = current_task.release_id

    # Running task

    update_release(release_id, "result", "RUNNING")
    log.info(f"Started release {release_name} to run single step {step_num}.")
    update_task(task_id, "status", "RUNNING")
    log.info(f"Started task with release_name {release_name} and step_num {step_num}.")

    curr_job_manager = BashJobManager(release_name)
    os.environ["RELEASE_VERSION"] = release_name
    status_code = curr_job_manager.run_job(current_task.step_num)

    # task status updating

    if status_code == 0:
        update_task(task_id, "status", "SUCCESS")
        log.info(f"Task #{step_num} of release {release_name} SUCCESS.")
        post_slack(f"Task #{step_num} of release {release_name} SUCCESS.")
    else:
        update_task(task_id, "status", "FAILED")
        log.info(f"Task #{step_num} of release {release_name} FAILED with code {status_code}.")
        slack_response = (
            f"Task #{step_num} of release {release_name} FAILED with code {status_code}.\n"
            f"{curr_job_manager.check_result_of_job(step_num)}"
        )
        print(slack_response)
        post_slack(slack_response)
        update_release(release_id, "result", "PAUSED")
        log.info(f"Release {release_name} stopped on task #{step_num}.")

    # Release status updating

    release_statuses = [str(s.status) for s in get_release_tasks(release_id)]
    if set(release_statuses) == {"SUCCESS"}:
        update_release(release_id, "result", "RELEASED")
        log.info(f"Successfully completed release {release_name}.")
        post_slack(f"Successfully completed release {release_name}.")

    return JSONResponse(content={
        "release_name": release_name, 
        "step_num": step_num, 
        "status": "SUCCESS" if status_code == 0 else "FAILED"
        })


@app.put("/thor-admin/clear")
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

@app.put("/thor-admin/reseed")
async def reseed():
    """ Reseeds data using the native reseed() and test data. """
    ctrs.reseed()
    log.info("Successfully reseeded data.")
    return JSONResponse(content={"status": "Success."})
