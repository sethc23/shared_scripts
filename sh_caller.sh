#!/bin/bash

SCRIPTS=/Users/admin/.scripts

source /Users/admin/.virtualenvs/devenv/bin/activate
cd $SCRIPTS
python $SCRIPTS/$1.py