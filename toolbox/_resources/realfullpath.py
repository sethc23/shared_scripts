#!/Users/admin/.virtualenvs/devenv/bin/python

import os
from subprocess import Popen as sub_popen
from subprocess import PIPE as sub_PIPE

def check_for_link(_path):
    cmd = "readlink %s" % _path
    p = sub_popen(cmd,stdout=sub_PIPE,shell=True)
    (_out,_err) = p.communicate()
    assert _err is None
    return _out.strip('\n')

def get_real_path(p):
    if not p[0]=='/':
        p = os.path.abspath(p)
    fpath = "/"
    mount_pt = ""
    for seg in p.split('/')[1:]:
        chk_path = os.path.join(fpath,seg)
        if os.path.ismount(chk_path):
            mount_pt = chk_path
        link_dest = check_for_link(chk_path)
        if link_dest:

            if os.path.isabs(mount_pt):

                if os.path.isabs(link_dest):
                    fpath = mount_pt + link_dest
                else:
                    fpath = os.path.join(mount_pt,link_dest)

            else:
                fpath = os.path.join(fpath,link_dest)

            fpath = get_real_path(fpath)

        else:
            fpath = os.path.join(fpath,seg)

    return fpath

def main(p):
    print get_real_path(p)


if __name__ == '__main__':
    import sys
    main(sys.argv[1])