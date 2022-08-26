# #!/bin/bash -x  

# Completely running gen3 load tests using Jenkins. 

pip install --upgrade pip
export CRYPTOGRAPHY_DONT_BUILD_RUST=1

poetry install
poetry run python3 jenkins-jobs-scripts/step7/gen3-run-load-tests.py &
pid = $!
wait $pid
