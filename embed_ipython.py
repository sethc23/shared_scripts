
from os import environ as os_env
from sys import path as py_path
py_path.append('%s/ipython/ipython' % os_env['SERV_HOME'])
from IPython import embed_kernel as embed
## not working -- from ipdb import set_trace as i_trace

# Usage:
#   from os import environ as os_environ
#   from sys import path as py_path
#   py_path.append(os_environ['HOME'] + '/.scripts')
#   import embed_ipython as I; I.embed()




#import embed_ipython as I; I.start_ipython(argv=["qtconsole","--profile=nbserver"]);

