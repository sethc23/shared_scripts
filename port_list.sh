#!/bin/bash

sudo lsof -n -i -P | grep LISTEN | grep -E '(nginx|syslog-ng|postgres|supervisor|uwsgi|ipython|rsync|redis|postfix|master|pycharm)' | awk '{printf ("%s\t%s\t%s\t%s\n", $1,$2,$3,$9) }' |  column -t