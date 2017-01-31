#!env python
from subprocess import Popen as sub_popen
from subprocess import PIPE as sub_PIPE
FROM_MAIN=False

def run_cmd(cmd,executable='/bin/zsh',verbose=True,FROM_MAIN=FROM_MAIN):
    p = sub_popen(cmd
                  ,stdout=sub_PIPE
                  ,shell=True
                  ,executable=executable)
    (_out,_err) = p.communicate()
    assert _err is None
    res = _out.rstrip('\n')
    if verbose:
        print(res)
    if not FROM_MAIN:
        return res
def growl(msg):
    growl = ' '.join(['timeout --kill-after=5 4s',
                    'ssh mbp2 -F /home/ub2/.ssh/config',
                    '"/usr/local/bin/growlnotify --sticky --message \'%s\'"'])
    run_cmd(growl % msg)
    raise SystemExit



# Dynamically call functions
if __name__ == '__main__':
    FROM_MAIN=True
    from sys import argv
    args = argv[1:]

    if not args:
        raise SystemExit,"Expecting input args instead of 'None'"
    else:
        import sys
        if len(args)>1:
            if type(args[-1])==dict:
                getattr(sys.modules[__name__],args[0])(args[1:-1],args[-1])
            else:
                getattr(sys.modules[__name__],args[0])(args[1:])
        else:
            # getattr(sys.modules[__name__],args[0])()
            run_cmd(args[0])
    a=0