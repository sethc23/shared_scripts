from subprocess                     import Popen            as sub_popen
from subprocess                     import PIPE             as sub_PIPE


def exec_cmds(*args,**kwargs):
    def run_cmd(args):
        cmd                             =   ' '.join(args.cmds)
        if args.cmd_host==args.cmd_worker:
            p                           =   sub_popen(cmd,stdout=sub_PIPE,shell=True)
        else:
            cmd                         =   "ssh %s '%s'" % (args.cmd_host,cmd)
            p                           =   sub_popen(cmd,stdout=sub_PIPE,shell=True)
        return p.communicate()

    if not hasattr(self,'T'):
        from py_classes                 import To_Class
        self.T                          =   To_Class({})
    for k,v in kwargs.iteritems():
        self.T.update(                      { 'kw_' + k                 :   v})

    if ( not hasattr(self.T,'kw_return_output')
        and not os_environ.has_key('in_args') ):
        self.T.update(                      { 'kw_return_output'        :   True})

    if type(args)==tuple:
        D                               =   argparse.Namespace()

        argh_args,arg_list              =   getattr(self.exec_cmds,'argh_args'),[]
        for it in argh_args:
            _default                    =   '' if not it.has_key('default') else it['default']
            this_arg                    =   it['option_strings'][-1].strip('-')
            arg_list.append(                this_arg)
            setattr(                        D,this_arg,_default)

        for i in range(len(args)):
            setattr(                        D,arg_list[i],args[i])

        for k,v in kwargs.iteritems():
            setattr(                        D,k,[v] if D.__dict__.has_key(k) and type(getattr(D,k)) is list else v)

        args                            =   D

    args.cmds                           =   args.cmds if type(args.cmds) is list else [args.cmds]
    if (not ' '.join(args.cmds).count('sudo')
        and not (hasattr(args,'root') and args.root==True)):
        return run_cmd(args)

    else:
        if not hasattr(self.T,'dt'):
            from datetime               import datetime as dt
            self.T.dt                   =   dt

        self.process                    =   args.tag
        self.process_start              =   self.T.dt.now()
        self.process_params             =   {'cmd'                      :   args.cmds}


        # cmds                          =   ['echo "%s" | sudo -S -k --prompt=\'\' ' % PASS,
        #                                    'bash -i -l -c "%s";' % cron_cmd]
        args.cmds                       =   [''.join(["SCR_OPT=$(if [ -n $(env | grep -E '^HOME' | grep 'Users/admin') ];",
                                             ' then echo "-qc"; else echo "-q"; fi;);']),
                                             'echo "%s" | sudo -S --prompt=\'\' ' % PASS,
                                             'script $SCR_OPT \"bash -i -l -c \'',
                                             '%s' % ' '.join(args.cmds).replace(';','\\;'),
                                             '\'\" | tail -n +2;',
                                             'echo "%s" | sudo -S --prompt=\'\' rm -f typescript;' % PASS,
                                             'unset SCR_OPT;',
                                            ]
        (_out,_err)                     =   run_cmd(args)
        _out                            =   _out.rstrip('\r\n')
        if hasattr(self.T,'kw_return_output'):
            return _out,_err
        self.process_end                =   self.T.dt.now()
        self.process_stout              =   _out
        self.process_sterr              =   _err
        if not self.process_sterr:
            results_and_errors          =   ['_'.join(['results'] + args.results)]   # default -> ['results_log']
        else:
            results_and_errors          =   ['_'.join(['errors'] + args.errors)]     # default -> ['errors_paste_log_txt']
        return System_Reporter().manage(    self,results_and_errors=results_and_errors)