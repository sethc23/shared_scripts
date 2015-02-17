
from subprocess import Popen as sub_popen
from subprocess import PIPE as sub_PIPE
from os.path import isdir

folders = ['/Volumes/mb/Users/admin',
           '/Volumes/mbp1/Users/admin',
           '/Volumes/mbp2/Users/admin']

for it in folders:
    if isdir(it):
        cmd         =   ['cp -R ~/.alias_shared %s/'%it]
        proc        =   sub_popen(cmd, stdout=sub_PIPE, shell=True)
        (t, err)    =   proc.communicate()
