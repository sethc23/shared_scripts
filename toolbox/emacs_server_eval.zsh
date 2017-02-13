#!/usr/local/bin/zsh

#[[ -z "$(echo $PATH|grep term|grep cmd)" ]] \
#    && export PATH=/Users/admin/.emacs.d/term-cmd:$PATH

#echo $PATH
#(echo $PATH)
#(open -a /Applications/Macports/Emacs.app "$@") &


/Applications/MacPorts/Emacs.app/Contents/MacOS/bin/emacsclient \
    -s $(lsof -U|grep emacs \
            |grep server|column -t \
            |tr -s ' '|cut -d ' ' -f8) \
    --eval $@ \
    > /dev/null 2>&1

