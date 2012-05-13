#!/bin/bash
echo "Opening $1"
python env_glsl.py $1 &
nano $1
kill %1
