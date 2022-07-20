import os
import sys
import json
import pathlib
import shutil

def run_shell(cmd):
    """
    Takes in the name of a shell script (string) and runs it. 
    Returns the status code as an int. 
    """
    status_code = os.system("sh " + cmd)
    return status_code

def identify_script_to_run(step_num):
    """
    Given the step number of a step, reads thor_config.json to figure out
    which shell script to run. Returns a full filepath to the script. 
    NOTE: Currently opening dummy_thor_config.json instead. 
    """
    with open("dummy_thor_config.json") as f:
        steps_dict = json.load(f)
    selected_step = [v for v in steps_dict.values() if v["step_num"] == int(step_num)][0]
    # print(selected_step)
    script_name = selected_step["script"]
    top_level_dir = os.getcwd() # Assumes this is being run from top-level /thor. 
    script_path = os.path.join(top_level_dir, "jenkins-jobs-scripts", \
        "step" + str(step_num), script_name)
    return script_path

def pull_job_params(step_num):
    """
    Given the step number, looks in thor_config.json to figure out
    which job parameters should be passed to the command. 
    Returns the job_params dict. 
    NOTE: As above, using dummy-thor-config.json instead. 
    """
    with open("dummy_thor_config.json") as f:
        steps_dict = json.load(f)
    selected_step = [v for v in steps_dict.values() if v["step_num"] == int(step_num)][0]
    job_params = selected_step["job_params"]
    return job_params


def attempt_to_run(step_num):
    """
    Given the step number of a step, tries to run the shell script associated with
    it as defined in thor_config.json. Returns the status code of the shell script.
    Will chdir into a temp 'workspace' directory before running the script, and
    will chdir back to the original directory after running the script.
    """
    top_level_dir = os.getcwd() # Assumes this is being run from top-level /thor. 
    if os.path.exists(top_level_dir + "/workspace"):
        shutil.rmtree(top_level_dir + "/workspace")
    os.mkdir(top_level_dir + "/workspace")

    script_to_run = identify_script_to_run(step_num)
    os.chdir(top_level_dir + "/workspace")
    status_code = run_shell(script_to_run)
    os.chdir(top_level_dir)

    return status_code


if __name__ == "__main__":
    # print(identify_script_to_run(sys.argv[1]))
    run_shell(sys.argv[1])
    # attempt_to_run(sys.argv[1])
    