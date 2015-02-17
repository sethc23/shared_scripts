#!/bin/bash

source ~/.bash_profile

underline="`tput smul`"
nounderline="`tput rmul`"
bold="`tput bold`"
normal=`tput sgr0`
red=`tput setaf 1`
green=`tput setaf 2`
yellow=`tput setaf 3`
default=`tput setaf 9`

echo ${yellow}${bold}$'\t\t\t'$1${default}
source /Users/admin/SERVER3/ipython/ENV/bin/activate
cd /Users/admin/SERVER3/.scripts
a=$(python System_Control.py check_health $1)
IFS='<>' read -a array <<< "$a"
eval echo "${array[@]}" | tr " " "\n"
$(`tput sgr0`)
