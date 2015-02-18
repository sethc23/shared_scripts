#!/bin/bash

source ~/.bashrc

underline="`tput smul`"
nounderline="`tput rmul`"
bold="`tput bold`"
normal=`tput sgr0`
red=`tput setaf 1`
green=`tput setaf 2`
yellow=`tput setaf 3`
default=`tput setaf 9`

echo ${yellow}${bold}$'\t\t\t'$1${default}
source $SERV_HOME/ipython/ENV/bin/activate
cd $HOME/.scripts
a=$(python System_Control.py check_health $1)
echo $a
IFS='<>' read -a array <<< "$a"
eval echo "${array[@]}" | tr " " "\n"
$(`tput sgr0`)
