#!/bin/bash -l

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
a=$(python System_Control.py check_health $1 )

eval $a

# NOTE:  running from terminal will always show "line 19: : command not found".
#        removing the inner sub-shell for each line output will fix the terminal error, BUT,
#		 GeekTool displays will have an 'm' at the end of certain lines due to issues with multiple tput commands

$(tput sgr0)
