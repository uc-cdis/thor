import os
import logging
import requests
import json
from pathlib import Path
import subprocess
import shutil

from thor.maestro.baton import JobManager

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)

DEVELOPMENT = os.getenv("DEVELOPMENT")

class BashJobManager(JobManager):
    def __init__(self, release_name):
        """
        Creates a Bash Job Manager
        """
        # use parent default

        self.release_name = release_name
        self.workspace_abs_path = ""

    def run_job(self, step_num):
        """
        Takes in the step_num of a step, and the list of parameters
        which need to be exposed as env variables. 
        Then, looks up in thor_config the shell script to run, and 
        runs it. 
        """
        log.info("Running bash job for step {}".format(step_num))
        script_path = self.identify_script_to_run(step_num)
        log.info("Executing script {}".format(script_path))
        if script_path == None:
            log.info("No script found for step {}".format(step_num))
            return 1
            # This forces the step to manually fail
        log.info("Script found for step {}".format(step_num))
        job_params = self.pull_job_params(step_num)

        if job_params == None:
            log.info("No job params found for step {}".format(step_num))
        else:
            log.info("Job params found for step {}".format(step_num))
            self.expose_env_vars(self.release_name, job_params)
            log.info("Env vars exposed for step {}".format(step_num))

        self.workspace_path = self.make_clean_workspace(step_num)
        os.chdir("./workspace/" + str(step_num))
        status_code = self.run_shell(script_path)
        os.chdir("../..")
        log.info("Status code for step {}: {}".format(step_num, status_code))
        return status_code
        
    def run_shell(self, cmd):
        """
        Takes in the name of a shell script (string) and runs it. 
        Returns the status code as an int. 
        Writes results (stdout, stderr) into a log file in the current directory.
        """
        logfile = open("logfile.txt", "w+")
        complete_process = subprocess.run(["bash", cmd], stdout=logfile, stderr=logfile)

        return complete_process.returncode

    def identify_script_to_run(self, step_num):
        """
        Given the step number of a step, reads thor_config.json to figure out
        which shell script to run. Returns a full filepath to the script. 
        NOTE: Looks at DEVELOPMENT to determine which config file to use.
        """
        if DEVELOPMENT:
            with open("dummy_thor_config.json") as f:
                steps_dict = json.load(f)
        else:
            with open("thor_config.json") as f:
                steps_dict = json.load(f)

        selected_step = [v for v in steps_dict.values() if v["step_num"] == int(step_num)][0]

        script_name = selected_step["script"]
        if script_name == None:
            return None
        top_level_dir = os.getcwd() # Assumes this is being run from top-level /thor. 
        script_path = os.path.join(top_level_dir, "release-task-scripts", \
            "step" + str(step_num), script_name)
        return script_path

    def pull_job_params(self, step_num):
        """
        Given the step number, looks in thor_config.json to figure out
        which job parameters should be passed to the command. 
        Returns the job_params dict. 
        NOTE: Looks at DEVELOPMENT to determine which config file to use.
        """
        if DEVELOPMENT == "true":
            with open("dummy_thor_config.json") as f:
                steps_dict = json.load(f)
        else:
            with open("thor_config.json") as f:
                steps_dict = json.load(f)
        selected_step = [v for v in steps_dict.values() if v["step_num"] == int(step_num)][0]
        job_params = selected_step["job_params"]
        return job_params

    def expose_env_vars(self, release_version, env_dict):
        """
        Given a dictionary of environment variables, sets the environment variables
        in the current shell. If passed something in JINJA form, will create 
        the relevant variable from the current release version. 
        """
        # Note: relies on 20XX.YY format for release_version. 
        if env_dict == None:
            return None
        for k, v in env_dict.items():
            if str(v).startswith("{{"):
                param_keyword = v.strip("{ }")
                if param_keyword.lower() == "release_version":
                    os.environ[k] = release_version
                elif param_keyword.lower() == "integration_branch":
                    os.environ[k] = "integration" + "".join(release_version.split("."))
            else:
                os.environ[k] = str(v)
        return None

    def make_clean_workspace(self, num_step: int):
        """
        Checks to see if there's a valid 'workspace' dir in the cwd. 
        If so, deletes and recreates it, otherwise, just creates it.
        """
        workspace_path = Path('./workspace')
        self.workspace_abs_path = workspace_path.resolve()
        workspace_path.mkdir(exist_ok=True)
        # Delete folder if exists and create a new folder
        folder_path = (workspace_path / str(num_step))
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            shutil.rmtree(folder_path)
        folder_path.mkdir()
        if DEVELOPMENT == "true":
            script_target_file_name = "workspace/shell_script_target.txt"
            target_absolute_path = os.path.join(os.getcwd(), script_target_file_name)
            if not os.path.exists(target_absolute_path):
                with open(target_absolute_path, "w") as target_file:
                    target_file.write("Shell Script Target\n\n")
        return None

    def check_result_of_job(self, job_name):
        """
        Tails the logs captured from the bash script
        job_name is the step number
        """
        if self.workspace_abs_path:
            with open(f"{self.workspace_abs_path}/{job_name}/logfile.txt", "r") as f:
                return "".join(f.readlines()[-1:])
    
    def get_job_status(self, job_name):
        return super().get_job_status(job_name)


if __name__ == "__main__":
    pass
