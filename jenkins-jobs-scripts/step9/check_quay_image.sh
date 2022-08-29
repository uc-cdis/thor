#!/bin/bash

pip install --upgrade pip
export CRYPTOGRAPHY_DONT_BUILD_RUST=1

/env/bin/python jenkins-jobs-scripts/step3/check_quay_image.py

