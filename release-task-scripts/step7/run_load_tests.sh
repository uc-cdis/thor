# #!/bin/bash -x  

# Running load tests using Github Actions workflow - https://github.com/uc-cdis/gen3-code-vigil/actions/workflows/load_tests.yaml. 

poetry run python /src/release-task-scripts/step7/run_load_tests.py
