#!/bin/bash

if [ -f $1 ]
then
  echo "Opening $1"
else
  echo "Creating a shader in '$1' from the template shader."
  cp default.template.glsl $1
fi

python env_glsl.py $1 &>/dev/null &
nano $1
kill %1
