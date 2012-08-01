#!/bin/bash

PY_SCRIPT=../execute.py
STEPS=5000

python $PY_SCRIPT 2  22 $STEPS &
python $PY_SCRIPT 22 42 $STEPS &
python $PY_SCRIPT 42 62 $STEPS &
python $PY_SCRIPT 62 82 $STEPS &

