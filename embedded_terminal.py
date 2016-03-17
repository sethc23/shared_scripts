from IPython.embedded.blockingkernelmanager import BlockingEmbeddedKernelManager
from IPython.zmq.blockingkernelmanager import BlockingKernelManager

# Note: ZMQTerminalInteractiveShell does not actually depend on ZMQ.
from IPython.frontend.terminal.console.interactiveshell import \
    ZMQTerminalInteractiveShell


def main():
    km = BlockingEmbeddedKernelManager()
    #km = BlockingKernelManager()
    km.start_kernel()
    km.start_channels()

    shell = ZMQTerminalInteractiveShell(kernel_manager=km)
    shell.mainloop()


if __name__ == '__main__':
    main()