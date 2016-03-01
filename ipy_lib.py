
def ib_k(a='get_ipython()'):
    
    import os
    from subprocess                     import Popen            as sub_popen
    from subprocess                     import PIPE             as sub_PIPE
    USER                                =   os.environ['USER']
    BASE_DIR                            =   os.environ['HOME'] + '/'

    def exec_cmds(cmds,cmd_host,this_worker):
        cmd                             =   ' '.join(cmds)
        if cmd_host==this_worker:
            p                           =   sub_popen(cmd,stdout=sub_PIPE,shell=True)
        else:
            cmd                         =   "ssh %s '%s'" % (cmd_host,cmd)
            p                           =   sub_popen(cmd,stdout=sub_PIPE,shell=True)
        return p.communicate()

    # 1. get info about kernel
    a                                   =   get_ipython()
    fpath                               =   a.kernel.config['IPKernelApp']['connection_file']
    fpath_in_mnt                        =   ''.join(['/Volumes/%s' % USER, fpath])
    # print fpath_in_mnt
    # fpath_shared                        =   fpath[fpath.find('.ipython'):]
    # fpath_in_mnt                        =   '/Volumes/%s/%s' % (USER,BASE_DIR) + fpath_shared
    (t, err)                            =   exec_cmds(["cat "+fpath],USER,USER)
    assert err==None
    k_info                              =   eval(t)
    # print k_info

    # 2. confirm access from REMOTE
    if not os.path.isdir('/Volumes/mbp2/Users/admin/.scripts'):          
        from System_Control             import System_Servers
        SERVS                           =   System_Servers()
        # from ipdb import set_trace as i_trace; i_trace()
        # print SERVS
        SERVS.mnt(['mbp2'])


    # if not os.path.isdir('/Volumes/mbp2/Volumes/%s' % USER):
    #     cmd                             =   ["python /Users/admin/.scripts/mounted_shares.py s3_always"]
    #     (t, err)                        =   exec_cmds(cmd,'mbp2',USER)
    #     assert err==None
    #     assert t==''

    # 3. create script on REMOTE for execution

    # ---- add cmds for opening proper ports
    cmds                                =   []
    for k,v in k_info.iteritems():
        if k.find('_port')!=-1:
            cmds.append(                    'ssh %s -X -f -N -L ' % USER + str(v) + ':localhost:' + str(v) + ';')

    # ---- add cmd for opening proper connection
    cmds.append(                            ' '.join(["$IPY/ENV/bin/ipython qtconsole",
                                                      "--profile=nbserver --matplotlib=qt5 --pprint --autoindent",
                                                      "--color-info --colors=linux --confirm-exit",
                                                      "--existing %s"%fpath_in_mnt+";"]))
    
    # ---- add cmds for closing connection
    for k,v in k_info.iteritems():
        if k.find('_port')!=-1:
            cmds.append("kill `ps -A | grep "+str(v)+":localhost:"+str(v)+" | grep -v grep | awk '{print $1}'`"+'; ')

    # ---- push cmds to REMOTE
    with open('/Volumes/mbp2/Users/admin/.scripts/k.sh','w') as f:
        for it in cmds:
            f.write(                        it+'\n')


    # 4. send ssh cmd for REMOTE execution of script
    # not sure sub_popen doesn't work...
    os.system(                                 "ssh -Xf mbp2 'cd $HOME/.scripts; ./k.sh &'")
    # cmd                                 =   ['cd $HOME/.scripts; ./k.sh &']
    # (t, err)                            =   exec_cmds(cmd,'mbp2',USER)
    # assert err==None
    # assert t==''


    return

if __name__ == '__main__':
    ib_k()