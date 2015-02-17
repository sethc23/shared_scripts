#!/bin/bash

SCRIPTS=/Users/admin/SERVER3/.scripts

source /Users/admin/SERVER3/ipython/ENV/bin/activate
cd $SCRIPTS
python $SCRIPTS/$1.py
