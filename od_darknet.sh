#!/bin/bash

export DYLD_LIBRARY_PATH=$HOME/code/ml/darknet:$DYLD_LIBRARY_PATH
python objectdetector.py objectdetector.yml

