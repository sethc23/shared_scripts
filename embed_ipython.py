
# from sys import path as py_path
# py_path.append('/home/ub2/SERVER2/ipython/ipython')
# from IPython import embed_kernel as embed
## not working -- from ipdb import set_trace as i_trace

# Usage:
#   from os import environ as os_environ
#   from sys import path as py_path
#   py_path.append(os_environ['HOME'] + '/.scripts')
#   import embed_ipython as I; I.embed()




#import embed_ipython as I; I.start_ipython(argv=["qtconsole","--profile=nbserver"]);


from __future__ import print_function
import os

from IPython.kernel.inprocess import InProcessKernelManager
from IPython.terminal.console.interactiveshell import ZMQTerminalInteractiveShell


def print_process_id():
    print('Process ID is:', os.getpid())


def main():
    print_process_id()

    # Create an in-process kernel
    # >>> print_process_id()
    # will print the same process ID as the main process
    kernel_manager = InProcessKernelManager()
    kernel_manager.start_kernel()
    kernel = kernel_manager.kernel
    kernel.gui = 'qt4'
    kernel.shell.push({'foo': 43, 'print_process_id': print_process_id})
    client = kernel_manager.client()
    client.start_channels()

    shell = ZMQTerminalInteractiveShell(manager=kernel_manager, client=client)
    shell.mainloop()

main()
if __name__ == '__main__':
    main()