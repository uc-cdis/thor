# #!/bin/bash -x  

# Completely running gen3 load tests using Jenkins. 

/env/bin/python jenkins-jobs-scripts/step7/gen3-run-load-tests.py &
pid = $!
wait $pid
