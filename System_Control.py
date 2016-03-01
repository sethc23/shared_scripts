#! ENV/bin/python
# PYTHON_ARGCOMPLETE_OK
# _ARC_DEBUG
"""

Manages Distributed Systems

"""

from system_settings                            import *
from system_argparse                            import *
from os                                         import environ                  as os_environ
from sys                                        import path                     as py_path
py_path.append(                                 os_environ['BD'])
from google_tools.google_main                   import Google

from pb_tools.pb_tools                          import pb_tools as PB
try:
    from ipdb import set_trace as i_trace   # i_trace()
    # ALSO:  from IPython import embed_kernel as embed; embed()
except:
    pass

class System_Build:

    def __init__(self):
        self.T                      =   System_Lib().T
        s                           =   System_Servers()
        self.servers                =   s.servers
        self.worker                 =   s.worker
        self.params                 =   {}
        self.Reporter               =   System_Reporter(self)
        self.pb                     =   PB().pb

    def configure_scripts(self,*vars):
        if len(vars)==0: cmd_host   =   self.worker
        else:            cmd_host   =   vars[0]

        cmds                        =   ['cd $HOME/.scripts;',
                                         'if [ -n "$(cat ENV/bin/activate | grep \'source ~/.bashrc\')" ]; then',
                                         'echo -e "\nsource ~/.bashrc\n" >> ENV/bin/activate;'
                                         'fi;']
        (_out,_err)                 =   self.T.exec_cmds({'cmds':cmds,'cmd_host':cmd_host,'cmd_worker':self.worker})
        assert _err==None
        assert _out==''

class System_Reporter:
    """Functions for uniformly managing output and error communications"""

    def __init__(self,_parent=None):
        self.T                              =   System_Lib().T if (not hasattr(self,'T') and not _parent) \
                                                else _parent.T if not hasattr(self,'T') else self.T
        locals().update(                        self.T.__dict__)
        # # DISABLED UPON LOADING REPORTER IN GOOGLE
        # s                                 =   System_Servers(self)
        # self.servers                      =   s.servers
        # self.worker                       =   s.worker
        # self.pb                             =   PB().pb
        # self.google                       =   Google()
        # self.GV                           =   self.google.Voice

    def __get_params(self):
        return                              [name for name,fx in inspect.getmembers(self,inspect.ismethod)
                                             if name.find('_') and not name.find('__')]

    def manage(self,admin,results_and_errors):
        """Input is taken from                 self.process,
                                            .process_start,
                                            .process_params,
                                            .process_stout,
                                            .process_sterr, and
                                            .process_end


            Assuming this class has already been initiated with:

                self.Reporter               =   System_Reporter(self)


            Usage [ e.g., at the end of a function ]:

                return self.Reporter.manage(    self,results_and_errors)


            Where 'results_and_errors' is a list
                with any one or more of the options:

                                                ['','results_print','results_log','results_log_txt',
                                                 'results_paste_log','results_paste_log_txt',
                                                 'errors_print','errors_log','errors_log_txt',
                                                 'errors_paste_log','errors_paste_log_txt']

            NOTE, if designations only exist for errors,
              no results are processed if self.process_sterr is empty.


            Template:

                self.process                =   ''
                self.process_start          =   dt.now()
                self.process_params         =   {}
                self.process_stout          =   []
                self.process_sterr          =   None
                self.process_end            =   dt.now()
                return self.Reporter.manage(    self,results_and_errors='')
        """
        NOTE_TO_DEVS = """
        Flow of function:

            1. If no sterr, ignore rules provided re: errors.
            2. Combine all rules into single Rule.
            3. Create Message.
            4. Process results with Message and according to Rule.

        """

        results_and_errors          =   results_and_errors if type(results_and_errors)==list else [results_and_errors]
        res,err                     =   [],[]
        for it in results_and_errors:
            if   it.find('results_')==0:
                res.append(             it.replace('results_','') )
            elif it.find('errors_')==0:
                err.append(             it.replace('errors_','') )

    #   1. If no stderr, (a) if only rules provided are for stderr, return
    #                    (b) if result rules, ignore stderr rules
        if not res and not err:
            return
        elif not res and not admin.process_sterr:
            return
        elif not admin.process_sterr:
            grp                             =   res
        else: grp                           =   res + err

    #   2. Combine all rules into single Rule.
        t                                   =   []
        for it in grp:
            t.extend(                           it.split('_') )
        methods                             =   dict(zip(t,range(len(t)))).keys()

    #   3. Create Message.
        runtime                             =   (admin.process_end-admin.process_start)
        if runtime.total_seconds()/60.0 < 1:
            runtime_txt                     =   'Runtime: %s seconds' % str(runtime.total_seconds())
        else:
            runtime_txt                     =   'Runtime: %s minutes' % str(runtime.total_seconds()/60.0)

        msg_title                           =   '[\"%s\" ENDED]' % admin.process
        msg                                 =   [msg_title,
                                                '',
                                                'Parameters: %s' % str(admin.process_params),
                                                 '',
                                                 'Started: %s' % dt.isoformat(admin.process_start),
                                                 runtime_txt,
                                                 '']
        msg_summary                         =   ', '.join([it for it in msg if it!=''])

        if res:
            if type(admin.process_stout)!=list:
                admin.process_stout         =   [ admin.process_stout ]
            if not (len(admin.process_stout)==0 or [None,'None','',[]].count(admin.process_stout)==1):
                msg.extend(                     ['Output: ',''])
                msg.extend(                     admin.process_stout )
                msg.extend(                     [''] )

        if err:
            if type(admin.process_sterr)!=list:
                admin.process_sterr         =   [ admin.process_sterr ]
            if not (len(admin.process_sterr)==0 or [None,'None','',[]].count(admin.process_sterr)==1):
                msg.extend(                     ['Errors: ',''] )
                msg.extend(                     admin.process_sterr )
                msg.extend(                     [''] )

        msg_str                             =   '\n'.join([str(it) for it in msg])

    #   4. Process results with Message and according to Rule.
        if methods.count('print')==1:
            self._print(                        msg)

        if methods.count('paste')==1:
            pb_url                          =   self._paste(msg_title,msg_str)
            log_msg                         =   ' - '.join([ msg_summary,pb_url ])
        else:
            log_msg                         =   msg_summary

        if methods.count('txt')==1:
            self._txt(                          log_msg)

        if methods.count('log')==1:
            self._log(                          log_msg)

        # ---

    def _print(self,msg):
        for it in msg:
            print it
        return

    def _paste(self,msg_title,msg_str):
        if not hasattr(self,'pb'):
            self.pb                         =   PB().pb
        pb_url                              =   self.pb.createPaste( msg_str,
                                                    api_paste_name=msg_title,
                                                    api_paste_format='',
                                                    api_paste_private='1',
                                                    api_paste_expire_date='1M')
        return pb_url

    def _g_txt(self,log_msg,phone_num='6174295700'):
        self.GV._msg(                           phone_num, log_msg)
        return

    def _txt(self,log_msg):
        opt                                 =   'F' if os_environ['USER']=='admin' else 't'
        cmd                                 =   'echo "%s" | mail -%s 6174295700@vtext.com' % (log_msg,opt)
        proc                                =   self.T.sub_popen(cmd, stdout=self.T.sub_PIPE, shell=True)
        (_out, _err)                        =   proc.communicate()
        assert _out==''
        assert _err==None
        return

    def _log(self,log_msg):
        cmd                                 =   'logger -t "System_Reporter" "%s"' % log_msg
        proc                                =   self.T.sub_popen(cmd, stdout=self.T.sub_PIPE, shell=True)
        (_out, _err)                        =   proc.communicate()
        assert _out==''
        assert _err==None
        return

    def _growl(self,log_msg,url=''):
        if url:
            cmd                             =   'growlnotify -m "%s" --url %s' % (log_msg,url)
        else:
            cmd                             =   'growlnotify -m "%s"' % log_msg
        self.T.exec_cmds(                       {'cmds':[cmd],'cmd_host':'mbp2','cmd_worker':self.T.THIS_PC})

class System_Lib:

    def __init__(self):
        import                                  sys
        import                                  codecs
        # reload(sys)
        # sys.setdefaultencoding('UTF8')
        from py_classes                     import To_Class
        from uuid                           import getnode                  as get_mac
        from os                             import system                   as os_cmd
        from sys                            import path                     as py_path
        from os                             import environ                  as os_environ
        from os                             import access                   as os_access
        from os                             import X_OK                     as os_X_OK
        from os                             import mkdir                    as os_mkdir
        import                                  inspect                     as I
        from traceback                      import format_exc               as tb_format_exc
        from types                          import NoneType
        from subprocess                     import Popen                    as sub_popen
        from subprocess                     import check_output             as sub_check_output
        from subprocess                     import PIPE                     as sub_PIPE
        from subprocess                     import STDOUT                   as sub_stdout
        import                                  shlex
        from time                           import sleep                    as delay
        from uuid                           import uuid4                    as get_guid
        from datetime                       import datetime                 as dt
        from dateutil                       import parser                   as DU
        from json                           import dumps                    as j_dump
        from re                             import findall                  as re_findall
        from sqlalchemy                     import create_engine
        import                                  logging
        logging.basicConfig()
        logging.getLogger(                      'sqlalchemy.engine').setLevel(logging.WARNING)
        import                                  pandas                      as pd
        import                                  psycopg2

        pd.set_option(                          'expand_frame_repr',False)
        pd.set_option(                          'display.max_columns', None)
        pd.set_option(                          'display.max_rows', 1000)
        pd.set_option(                          'display.width',180)
        np                                  =   pd.np
        np.set_printoptions(                    linewidth=200,threshold=np.nan)

        sys_eng                             =   create_engine(r'postgresql://postgres:postgres@%s:%s/%s'%(DB_HOST,DB_PORT,DB_NAME),
                                                    encoding='utf-8',
                                                    echo=False)

        conn                                =   psycopg2.connect("""dbname='%s' user='postgres'
                                                                    host='%s' password='' port=%s"""
                                                                 %(DB_NAME,DB_HOST,DB_PORT));
        cur                                 =   conn.cursor()

        D                                   =   {'exec_cmds'                :   System_Admin().exec_cmds,
                                                 'user'                     :   os_environ['USER'],
                                                 'guid'                     :   str(get_guid().hex)[:7]}
        D.update(                               {'tmp_tbl'                  :   'tmp_'+D['guid']})
        self.T                              =   To_Class(D)
        all_imports                         =   locals().keys()
        
        excludes                            =   ['D','self']
        for k in all_imports:
            if not excludes.count(k):
                self.T.update(                  {k                          :   eval(k) })
        
        import                                  system_settings             as ss
        self.T.update(                          ss.__dict__)
        self.T.Reporter                     =   System_Reporter(self)
        globals().update(                       self.T.__dict__)

class System_Admin:
    """Functions for operating administrative features"""

    def __init__(self):
        # import inspect as I
        # K = I.stack()
        
        # self.T                            =   System_Lib().T
        # T                                 =   self.T
        # locals().update(                      T.__dict__)
        # s                                 =   System_Servers()
        # self.servers                      =   s.servers
        # self.worker                       =   s.worker
        # self.Reporter                     =   System_Reporter(self)
        # from system_command import exec_cmds
        # self.exec_cmd_script = exec_cmds
        pass


    @arg('cmds',action=Store_List,help="a 'list' of command(s) to execute")
    @arg('-H','--cmd_host',nargs='?',default=os_environ['USER'],
         choices=parse_choices_from_pgsql("""
                                            select distinct server res
                                            from servers
                                            where server_idx is not null
                                            order by server
                                          """),
         help="server to execute CMDS")
    @arg('-W','--cmd_worker',nargs='?',default=os_environ['USER'],
         choices=parse_choices_from_pgsql("""
                                            select distinct server res
                                            from servers
                                            where server_idx is not null
                                            order by server
                                          """),
         help="server sending CMDS script to CMD_HOST")
    @arg('-T','--tag',nargs='?',default='exec_cmds',help='label to apply to authorization request for purposes of logging')
    @arg('-R','--results',nargs='*',
         default=['log'],
         choices                    =   [name.lstrip('_') for name,fx
                                         in inspect.getmembers(System_Reporter,inspect.ismethod)
                                         if (name.find('_')==0 and name.find('__')==-1)],
         help='options for handling RESULTS')
    @arg('-E','--errors',nargs='*',
         default=['paste','log','txt'],
         choices                    =   [name.lstrip('_') for name,fx
                                         in inspect.getmembers(System_Reporter,inspect.ismethod)
                                         if (name.find('_')==0 and name.find('__')==-1)],
         help='options for handling ERRORS (Note: No reporting if only ERRORS are defined and no error output)')
    def exec_cmds(self,args,**kwargs):
        """Executes commands and returns (_out,_err).\nNote, SSH is used when cmd_host!=this_worker"""
        def run_cmd(args):
            cmd                             =   ' '.join(args.cmds)
            if args.cmd_host==args.cmd_worker:
                p                           =   sub_popen(cmd,stdout=sub_PIPE,shell=True)
            else:
                cmd                         =   "ssh %s '%s'" % (args.cmd_host,cmd)
                p                           =   sub_popen(cmd,stdout=sub_PIPE,shell=True)
            return p.communicate(),p

        if not hasattr(self,'T'):
            from py_classes                 import To_Class
            self.T                          =   To_Class({})
        for k,v in kwargs.iteritems():
            self.T.update(                      { 'kw_' + k                 :   v})

        if ( not hasattr(self.T,'kw_return_output')
            and not os_environ.has_key('in_args') ):
            self.T.update(                      { 'kw_return_output'        :   True})

        if [tuple,dict,list].count(type(args)):
            D                               =   argparse.Namespace()

            argh_args,arg_list              =   getattr(self.exec_cmds,'argh_args'),[]
            for it in argh_args:
                _default                    =   '' if not it.has_key('default') else it['default']
                this_arg                    =   it['option_strings'][-1].strip('-')
                arg_list.append(                this_arg)
                setattr(                        D,this_arg,_default)

            if type(args)==dict:
                for k,v in args.iteritems():
                    setattr(                    D,k,v)
            elif [tuple,list].count(type(args)):
                for i in range(len(args)):
                    setattr(                    D,arg_list[i],args[i])

            for k,v in kwargs.iteritems():
                setattr(                        D,k,[v] if D.__dict__.has_key(k) and type(getattr(D,k)) is list else v)

            args                            =   D

        args.cmds                           =   args.cmds if [list,argparse.Namespace].count(type(args.cmds)) else [args.cmds]

        if len(args.cmds)>1:    args.cmds   =   [ it.rstrip(';') + ';' for it in args.cmds[:-1] ] + [ args.cmds[-1].rstrip(' ;') + ';' ]
        else:                   args.cmds   =   [args.cmds[0].rstrip(' ;') + ';']


        if (not ' '.join(args.cmds).count('sudo')
            and not (hasattr(args,'root') and args.root==True)):
            (_out,_err),p                   =   run_cmd(args)
            if hasattr(self.T,'kw_return_process') and self.T.kw_return_process:
                return (_out,_err),p
            else:
                return (_out,_err)

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
                                                 '%s' % ' '.join(args.cmds),  #.replace(';','\\;'),
                                                 '\'\" | tail -n +2;',
                                                 'echo "%s" | sudo -S --prompt=\'\' rm -f typescript;' % PASS,
                                                 'unset SCR_OPT;',
                                                ]
            (_out,_err),p                   =   run_cmd(args)
            _out                            =   _out.rstrip('\r\n')
            res                             =   []
            if hasattr(self.T,'kw_return_output') and self.T.kw_return_output:
                res.extend(                     [_out,_err])
            if hasattr(self.T,'kw_return_process') and self.T.kw_return_process:
                res.append(                     p)

            if res:
                return res
            
            self.process_end                =   self.T.dt.now()
            self.process_stout              =   _out
            self.process_sterr              =   _err
            if not self.process_sterr:
                results_and_errors          =   ['_'.join(['results'] + args.results)]   # default -> ['results_log']
            else:
                results_and_errors          =   ['_'.join(['errors'] + args.errors)]     # default -> ['errors_paste_log_txt']
            return System_Reporter().manage(    self,results_and_errors=results_and_errors)

class System_Backup:
    """Perform backup operations to select systems"""

    def __init__(self,_parent=None):
        self.T                              =   System_Lib().T if (not hasattr(self,'T') and not _parent) \
                                                    else _parent.T if not hasattr(self,'T') else self.T
        locals().update(                        self.T.__dict__)
        s                                   =   System_Servers()
        self.servers                        =   s.servers
        self.worker                         =   s.worker
        self.base_dir                       =   s.base_dir
        self.priority                       =   s.priority
        self.ready                          =   s.mnt(['ub2','ub1'])
        # self.cfg                            =   self.get_cfg()
        self.params                         =   {}
        # self.dry_run                        =   True
        self.dry_run                        =   False
        self.Reporter                       =   System_Reporter(self)
        self.pb                             =   PB().pb

    def __add_options(self):
        options                     =   [ 'verbose','verbose','recursive','archive','update',
                                          'one-file-system','compress','prune-empty-dirs',
                                          'itemize-changes']
                                        #,"filter='dir-merge /.rsync-filter'"]
			                            # ,'delete-before'
        if self.dry_run==True:          options.append('dry-run')
        self.params.update(             { 'options'     :   map(lambda s: '--%s'%s,options) })

    def __add_exclusions(self):
        exclude                     =   self.cfg.exclude.map(lambda s: '--exclude='+str(s)).tolist()
        if len(exclude)!=0:
            self.params.update(         { 'exclusions':   exclude, })

    def __add_inclusions(self):
        include                     =   self.cfg.include.map(lambda s: '--include='+str(s)).tolist()
        if len(include)!=0:
            self.params.update(         { 'inclusions':   include, })

    def __add_logging(self):
        self.params.update(             { 'logging'     :   ['--outbuf=L'], })

    def ipython(self,params=''):
        """OLD FUNC -- rsync ipython on ub2"""
        self.process                =   'backup_ipython'
        self.process_start          =   dt.isoformat(dt.now())
        self.add_options(               )
        self.add_exclusions(            )
        from_dir                    =   '/home/ub2/BD_Scripts/ipython'
        to_dir                      =   '/home/ub2/'
        src                         =   from_dir if self.worker=='ub2' else '/Volumes/ub2'+from_dir
        dest                        =   to_dir   if self.worker=='ub2' else '/Volumes/ub2'+to_dir
        self.params.update(             {'src_dir'      :   src,
                                         'dest_dir'     :   dest,
                                         'operation'    :   '%s: %s'%(self.worker,self.process)})
        self.run_rsync(                 )
        self.process_end            =   dt.isoformat(dt.now())
        return self.to_pastebin(        )

    @arg()
    def databases(self,args):
        """Backup all pgSQL databases as identified in the 'databases' pgSQL table"""
        self.process                        =   'backup_databases'
        self.process_start                  =   self.T.dt.now()
        self.process_params                 =   {}
        self.process_stout                  =   []
        d                                   =   System_Databases()
        self.databases                      =   d.databases
        self.database_names                 =   self.databases.db_name.tolist()
        for i in range(len(self.databases)):
            T                               =   {'started'                  :   dt.isoformat(dt.now())}
            db_info                         =   self.databases.ix[i,['backup_path','db_server','db_name','backup_cmd']].map(str)

            serv_info                       =   self.servers[self.servers.git_tag==db_info['db_server']].iloc[0,:].to_dict()

            T.update(                           {'DB'                       :   '%s @ %s' % (db_info['db_name'],
                                                                                     serv_info['server'])})

            fpath                           =   '%s/%s_%s_%s.sql' % tuple(db_info[:-1].tolist() + [dt.strftime(dt.now(),'%Y_%m_%d')])
            fname                           =   fpath[fpath.rfind('/')+1:]
            cmd                             =   """%s -d %s -h 0.0.0.0 -p 8800 --username=postgres > %s 2>&1
                                                """.replace('\n','').replace('\t','').strip() % (db_info['backup_cmd'],
                                                                                                 db_info['db_name'],
                                                                                                 fpath)
            (_out,_err)                     =   exec_cmds({'cmds':[cmd],'cmd_host':serv_info['server'],'cmd_worker':self.worker})
            T.update(                           {   'stdout'                :   _out })
            assert _err==None

            cmds                            =   ['scp %(host)s@%(serv)s:%(fpath)s /Volumes/EXT_HD/.pg_dump/;'
                                                 % ({ 'host'                :   serv_info['host'],
                                                      'serv'                :   serv_info['server'],
                                                      'fpath'               :   fpath })]

            (_out,_err)                     =   exec_cmds({'cmds':cmds,'cmd_host':'ub1','cmd_worker':self.worker})
            assert _out==''
            assert _err==None

            T.update(                           {   'ended'             :   dt.isoformat(dt.now())} )

            self.process_stout.append(          T )

        self.process_sterr                  =   None
        self.process_end                    =   dt.now()
        return self.Reporter.manage(            self,results_and_errors=['results_paste_log'])

    def system(self,params=''):
        """OLD FUNC -- rsync all servers to external HD"""
        self.cfg                        =   self.get_cfg()
        self.process                    =   'backup_system'
        self.process_start              =   dt.isoformat(dt.now())
        self.add_options(                   )
        self.add_exclusions(                ) # DON'T ADD INCLUSIONS -- see sync_items below
        cfg                             =   self.cfg
        cols                            =   cfg.columns.map(str).tolist()
        t_cols                          =   [it for it in cols if it[0].isdigit()]

        grps,pt                         =   [],0
        for i in range(len(t_cols)/2):
            x                           =   cfg[[t_cols[pt],t_cols[pt+1],'include']].apply(lambda s: [str(s[0])+'-'+str(s[1]),str(s[2])],axis=1).tolist()
            grps.extend(                    x   )
            pt                         +=   2
        res                             =   [it for it in grps if (str(it).find("['-',")==-1 and str(it).find("'']")==-1) ]
        d                               =   pd.DataFrame({  'server_pair'       :   map(lambda s: s[0],res),
                                                        'transfer_files'    :   map(lambda s: s[1],res)})
        _iters                          =   d.server_pair.unique().tolist()
        for pair in _iters:
            sync_items                  =   d[d.server_pair==pair].transfer_files
            incl                        =   sync_items.map(lambda s: ' --include='+s).tolist()
            a,b                         =   pair.split('-')
            a_serv,b_serv               =   map(lambda s: str(self.servers[self.servers.tag==s].server.iloc[0]),pair.split('-'))
            a_dir,b_dir                 =   map(lambda s: str(self.servers[self.servers.tag==s].home_dir.iloc[0]),pair.split('-'))
            # _host                     =    b if priority[a]>priority[b] else a
            src                         =   a_dir if a_serv==self.worker else '/Volumes/'+a_serv+a_dir
            dest                        =   b_dir if b_serv==self.worker else '/Volumes/'+b_serv+b_dir
            for it in sync_items:
                self.params.update(         {'src_dir'      :   src+'/'+it.lstrip('/'),
                                             'dest_dir'     :   dest+'/',
                                             'operation'    :   '%s: %s -- %s -- %s'%(self.worker,self.process,pair,it)})
                self.run_rsync(             )
        self.process_end                =   dt.isoformat(dt.now())
        return self.to_pastebin(            )


    @arg('lib',nargs='+',default='ALL',choices=parse_choices_from_pgsql("""
                                                                select json_object_keys(pip_libs::json) res
                                                                from servers
                                                                where pip_libs is not null
                                                                and server ilike '%s'
                                                             """,['--target']) + ['ALL'],
        help='known pip libs to backup\n(list avail. when target included)')
    @arg('target',nargs='?',default=os_environ['USER'],choices=parse_choices_from_pgsql("""
                                                                select distinct server res
                                                                from servers
                                                                where server_idx is not null
                                                                order by server
                                                             """),
        help='target server on which to backup pip')
    def pip(self,args):
        """Backup specific pip library requirements from a specified server to pgSQL"""

        SERVS                               =   args.target if not args.target=='ALL' \
                                                else self.servers[self.servers.pip_libs.isnull()==False].server.tolist()
        SERVS                               =   SERVS if type(SERVS) is list else [SERVS]
        spec_libs                           =   args.lib if args.lib else []

        self.process                        =   'backup_pip'
        self.process_start                  =   dt.now()
        self.process_params                 =   {'SERVS'             :   SERVS }
        self.process_stout                  =   []

        for serv in SERVS:
            libs,skip_libs                  =   {},{}
            if len(spec_libs)==0 or spec_libs=='ALL':
                libs                        =   self.servers[ self.servers.tag==serv ].pip_libs.tolist()[0]
            else:
                all_libs                    =   self.servers[ self.servers.tag==serv ].pip_libs.tolist()[0]
                for it in all_libs.keys():
                    if spec_libs.count(it)>0 or spec_libs==['ALL']:
                        libs.update({           it                  :   all_libs[it] }  )
                    else:
                        skip_libs.update({      it                  :   all_libs[it] }  )

            self.process_stout.append(          { '%s_pip_libs'%serv  :   str(libs) })

            D,old_reqs                      =   {},[]
            for k,v in libs.iteritems():

                if v['requirements']!='':
                    old_reqs.append(            v['requirements'].replace('http://pastebin.com/','')  )

                lib_loc                     =   v['location']
                cmds                        =   ['cd %s' % lib_loc]
                if lib_loc.find('ENV')>0:
                    cmds.append(                'source bin/activate'  )
                cmds.append(                    'pip freeze'  )

                cmd                         =   '; '.join(cmds)
                if serv!=self.worker:
                    cmd                     =   "ssh %s '%s'" % (serv,cmd)

                proc                        =   sub_check_output(cmd, stderr=sub_stdout, shell=True)

                pb_url                      =   self.pb.createPaste(proc,
                                                                    api_paste_name='%s -- pip_lib: %s' % (serv,k),
                                                                    api_paste_format='',
                                                                    api_paste_private='1',
                                                                    api_paste_expire_date='N')

                D.update(                       { k     :   {'location'     :   lib_loc,
                                                             'requirements' :   pb_url }
                                                })

                # Append any libs not updated
                for k,v in skip_libs.iteritems():
                    D.update(                   { k     :   v }  )

                # Push to servers DB
                cmd                         =   """
                                                    UPDATE servers SET
                                                    pip_libs            =   '%s',
                                                    pip_last_updated    =   'now'::timestamp with time zone
                                                    WHERE tag = '%s'
                                                """ % (j_dump(D),serv)

                conn.set_isolation_level(       0)
                cur.execute(                    cmd   )

                # Delete old Pastes
                for it in old_reqs:
                    self.pb.deletePaste(        it)

        self.process_sterr                  =   [None]
        self.process_end                    =   dt.now()

        return self.Reporter.manage(            self,results_and_errors=['results_paste_log'])

    def __to_pastebin(self,params=''):
        if self.dry_run==True:          return True
        else:

            condition                   =   """
                                                operation ilike '%s: %s%s'
                                                and started >=  '%s'::timestamp with time zone
                                                and ended   <  '%s'::timestamp with time zone
                                            """ % (self.worker,self.process,'%%',
                                               self.process_start,self.process_end)

            df                          =   pd.read_sql("select * from system_log where %s" % condition,sys_eng)

            T                           =   df.iloc[0].to_dict()
            T['operation']              =   '%s: %s' % (self.worker,self.process)
            pb_url                      =   self.pb.createPaste(df.to_html(), api_paste_name = T['operation'],
                                                          api_paste_format = 'html5', api_paste_private = '1',
                                                          api_paste_expire_date = '2W')

            T['stout']                  =   pb_url
            T['ended']                  =   dt.isoformat(dt.now())
            T['parameters']             =   '\n\n'.join(df.parameters.tolist()).replace("'","''")
            c                           =   """insert into system_log values ('%(operation)s','%(started)s',
                                                              '%(parameters)s','%(stout)s',
                                                              '%(sterr)s','%(ended)s')"""%T
            conn.set_isolation_level(       0)
            cur.execute(                    c   )

            conn.set_isolation_level(       0)
            cur.execute(                    "delete from system_log where %s " % condition  )
            return True

    def __run_rsync(self):
        c,keys                          =   ['rsync'],self.params.keys()
        if keys.count('options'):           c.extend(self.params['options'])
        if keys.count('inclusions'):        c.extend(self.params['inclusions'])
        if keys.count('exclusions'):        c.extend(self.params['exclusions'])
        if keys.count('logging'):           c.extend(self.params['logging'])

        c.extend([                          self.params['src_dir'], self.params['dest_dir'] ])
        cmd                             =   ' '.join(c)
        start_ts                        =   dt.isoformat(dt.now())
        proc                            =   sub_popen([cmd], stdout=sub_PIPE, shell=True)
        (t, err)                        =   proc.communicate()
        c                               =   "insert into system_log values ('%s','%s','%s','%s','%s','%s')"%(
                                            self.params['operation'],start_ts,
                                            '%s %s'%(self.params['src_dir'],self.params['dest_dir']),
                                            unicode(t).replace("'","''"), unicode(err).replace("'","''"), dt.isoformat(dt.now()))
        conn.set_isolation_level(           0)
        cur.execute(                        c)
        return True

class System_Build:
    """Functions for building certain systems"""

    def __init__(self):
        self.T                      =   System_Lib().T
        s                           =   System_Servers()
        self.servers                =   s.servers
        self.worker                 =   s.worker
        self.params                 =   {}
        self.Reporter               =   System_Reporter(self)
        self.pb                     =   PB().pb

    def configure_scripts(self,*vars):
        """Function to configure bash environment"""
        if len(vars)==0: cmd_host   =   self.worker
        else:            cmd_host   =   vars[0]

        cmds                        =   ['cd $HOME/.scripts;',
                                         'if [ -n "$(cat ENV/bin/activate | grep \'source ~/.bashrc\')" ]; then',
                                         'echo -e "\nsource ~/.bashrc\n" >> ENV/bin/activate;'
                                         'fi;']
        (_out,_err)                 =   exec_cmds({'cmds':cmds,'cmd_host':cmd_host,'cmd_worker':self.worker})
        assert _err==None
        assert _out==''

    @arg('target',nargs='?',default=os_environ['USER'],choices=parse_choices_from_pgsql("""
                                                                select distinct server res
                                                                from servers
                                                                where server_idx is not null
                                                                order by server
                                                             """),
        help='target server on which to install pip library')
    @arg('target_path',default='./ENV',
        help='path on target server to install pip library')
    @arg('source',nargs='?',default=os_environ['USER'] if len(in_args)<4 else in_args[3],
        choices=parse_choices_from_pgsql("""
                                            select distinct server res
                                            from servers
                                            where pip_libs is not null
                                            order by server
                                         """),
        help='server source to copy pip requirements from')
    @arg('source_lib',nargs='?',
        choices='(choices will appear when SOURCE specified)' if len(in_args)<6 else 
            parse_choices_from_pgsql("""
                                        select json_object_keys(pip_libs::json) res
                                        from servers
                                        where server = '%s'
                                     """ % ('' if len(in_args)<6 or in_args[5][0]=='-' else in_args[5])),
        help='pip library on server source to install on target server at target_path')
    @arg('--overwrite',action='store_true',help='remove existing virtualenv (if applicable) and install')
    @arg('--upgrade',action='store_true',help='ignore versions in saved requirements data and install the latest libraries')
    @arg('-R','--results',action='append',
         default=['log'],
         choices                    =   [name.lstrip('_') for name,fx
                                         in inspect.getmembers(System_Reporter,inspect.ismethod)
                                         if (name.find('_')==0 and name.find('__')==-1)],
         help='options for handling RESULTS')
    @arg('-E','--errors',action='append',
         default=['paste','log','txt'],
         choices                    =   [name.lstrip('_') for name,fx
                                         in inspect.getmembers(System_Reporter,inspect.ismethod)
                                         if (name.find('_')==0 and name.find('__')==-1)],
         help='options for handling ERRORS (Note: No reporting if only ERRORS are defined and no error output)')
    def install_pip(self,args):
        """Install pip libraries using pip requirements saved in pgSQL"""
        self.process                    =   'install_pip'
        self.process_start              =   dt.now()

        to_serv,to_path                 =   args.target,args.target_path
        serv                            =   self.servers[self.servers.tag==to_serv].iloc[0,:].to_dict()
        to_path                         =   to_path % serv
        to_path                         =   to_path if not to_path[-1]=='/' else to_path+'ENV'

        to_dir,env_dir                  =   to_path[:to_path.rfind('/')],to_path[to_path.rfind('/')+1:]
        from_serv,from_lib              =   args.source,args.source_lib

        self.process_params             =   {'to_serv'          :   to_serv,
                                             'to_path'          :   to_path,
                                             'from_serv'        :   from_serv,
                                             'from_lib'         :   from_lib,
                                             'overwrite'        :   args.overwrite,
                                             'upgrade'          :   args.upgrade,}

        z                               =   pd.read_sql("select pip_libs from servers where tag = '%s'"%from_serv,sys_eng)
        t                               =   z.pip_libs.tolist()[0][from_lib]['requirements']

        reqs                            =   self.pb.getPasteRawOutput(t[t.rfind('/')+1:]).split('\n')
        if args.upgrade:
            version_spec                =   '>='
            reqs                        =   [it.replace('==',version_spec) for it in reqs if it.find('==')!=-1]
        else:
            version_spec                =   '=='
            reqs                        =   [it for it in reqs if it.find('==')!=-1] #running this ensure only libs included


        master_order                    =   ['numpy','Cython']
        libs                            =   map(lambda s: s[:s.find(version_spec)],reqs)
        lib_versions                    =   map(lambda s: s[s.find(version_spec):],reqs)
        lib_vers_D                      =   dict(zip(libs,lib_versions))
        master_order.reverse()
        for it in master_order:
            if libs.count(it)>0:
                _lib                    =   libs.pop(libs.index(it))
                libs.insert(                0,_lib)
        new_reqs                        =   map(lambda s: s+lib_vers_D[s],libs)
        assert sorted(reqs)==sorted(new_reqs)
        reqs                            =   new_reqs

        cmds                            =   ['rm -fR /tmp/install_env;',
                                            'pip --version;',
                                            'virtualenv --version;',
                                            'if [ ! -d "%s" ]; then echo "DEST PATH NOT EXIST" && exit 1; fi;' % to_dir]
        if not args.overwrite:
            cmds.append(                    'if [ -d "%s" ]; then echo "DEST PATH ALREADY EXISTS" && exit 1; fi;' % to_path)


        (_out,_err)                     =   exec_cmds({'cmds':cmds,'cmd_host':to_serv,'cmd_worker':self.worker})
        assert _err==None
        assert _out.find('No such file or directory')==-1
        assert _out.find('command not found')==-1
        assert _out.find('DEST PATH NOT EXIST')==-1
        assert _out.find('DEST PATH ALREADY EXISTS')==-1

        script                          =   ['#!/bin/bash',
                                             'echo "install_env started"',
                                             'cd %s' % to_dir]

        if args.overwrite:
            script.append(                  'rm -fR %s/' % env_dir)

        script.extend(                      ['virtualenv ENV || exit 1',
                                             'source ENV/bin/activate  || exit 1',
                                             'pip install --upgrade pip || exit 1'] )

        line_cmd                        =   ' '.join(['pip install --allow-all-external --allow-unverified %(lib)s',
                                                      '%(lib_v)s',
                                                      '|| echo "Error installing %(lib)s"'])

        script.extend(                      [ line_cmd % {'lib':it[:it.find(version_spec)],'lib_v':it} for it in reqs ])
        script.extend(                      ['echo "install_env complete"'])
        with open('/tmp/install_env','w') as f:
            f.write(                        '\n'.join(script))

        os_cmd(                             'chmod +x /tmp/install_env')

        if to_serv!=self.worker:
            cmds                        =   ['scp %s:/tmp/install_env /tmp/ 2>&1;' % (self.worker),
                                             '/tmp/install_env 2>&1 || exit 1;',
                                             'rm /tmp/install_env;']
            (_out,_err)                 =   exec_cmds({'cmds':cmds,'cmd_host':to_serv,'cmd_worker':self.worker})
        else:
            (_out,_err)                 =   exec_cmds({ 'cmds':['/tmp/install_env 2>&1','rm /tmp/install_env'],
                                                        'cmd_host':self.worker,'cmd_worker':self.worker})

        assert _err==None
        assert _out.count('install_env started')==1
        assert _out.count('install_env complete')==1
        os_cmd(                         'rm /tmp/install_env;')

        self.process_end                =   dt.now()

        errors                          =   []
        for it in _out.split('\n'):
            if it.find('Error installing ')==0:
                errors.append(              it.replace('Error installing ',''))

        self.process_stout              =   None
        if len(errors)==0:
            self.process_sterr          =   None
        else:
            self.process_sterr          =   'Errors installing [%s]' % ','.join(errors)

        if not self.process_sterr:
            self.process_stout.append(  'Repos look good' )
            results_and_errors          =   ['_'.join(['results'] + args.results)]   # default -> ['results_log']
        else:
            results_and_errors          =   ['_'.join(['errors'] + args.errors)]     # default -> ['errors_paste_log_txt']

        return self.Reporter.manage(    self,results_and_errors=results_and_errors)

    def sync_pip(self,vars):
        """
        Usage:                      [control] [actor] [actor_scope] [params]


            python System_Control.py sync pip_lib all .scripts
            python System_Control.py sync pip_lib all .scripts ub1 ub2 mbp2
            python System_Control.py sync pip_lib update ub1 BD_Scripts mbp2 BD_Scripts
            python System_Control.py sync pip_lib merge ub1 BD_Scripts mbp2 BD_Scripts

        Caveat(s):

            Libraries must exist unless 'all' option used.

        """
        pass
        self.process_end            =   dt.now()

class System_Config:
    """Functions for getting and setting system configurations"""

    def __init__(self):
        """

            Entry Format: [ {settings directory},{settings file},{cmd to reset program settings} ]

        """
        self.T                      =   System_Lib().T
        locals().update(                self.T.__dict__)
        D                           =   {'aprinto'  :   ['%(SERV_HOME)s/aprinto',
                                                         'aprinto_settings.py'],
                                         'gitserv'  :   ['%(GIT_SERV_HOME)s/celery/git_serv',
                                                         'git_serv_settings.py'],
                                         'nginx'    :   ['%(SERV_HOME)s/nginx/setup/nginx/sites-available',
                                                         'run_aprinto.conf',
                                                         ' '.join(['echo "%(PASS)s" | sudo -S -k --prompt=\'\'',
                                                                   'sh -c "%(SERV_HOME)s/nginx/push_ng_config.bash;',
                                                                   'nginx -s reload -p %(SERV_HOME)s/run -c',
                                                                   '/usr/local/openresty/nginx/conf/nginx.conf -g',
                                                                   '\\"user %(ROOT)s %(ROOT_GRP)s; pid',
                                                                   '%(SERV_HOME)s/run/pids/sv_nginx.pid; daemon on;\\"";'])
                                                         ],
                                         'hosts'    :   ['/etc','hosts']
                                        }
        os_environ.update(              {'PASS'     :   PASS})
        self.auth                   =   'echo "%(PASS)s" | sudo -S -k --prompt=\'\' ' % os_environ + 'sh -c "%(cmd)s";'
        self.D                      =   D

    def get_cfg(self):
        base                        =   self.base_dir if self.worker=='ub2' else '/Volumes/ub2'+self.base_dir
        cfg_fpath                   =   base + '/BD_Scripts/files_folders/rsync/backup_system_config.xlsx'
        cfg                         =   pd.read_excel(cfg_fpath, na_values ='', keep_default_na=False, convert_float=False)
        cols                        =   cfg.columns.tolist()
        cols_lower                  =   [str(it).lower() for it in cols]
        cfg.columns                 =   [cols_lower]
        for it in cols_lower:
            cfg[it]                 =   cfg[it].map(lambda s: '' if str(s).lower()=='nan' else s)
        tbl                         =   'config_rsync'
        conn.set_isolation_level(       0)
        cur.execute(                    'drop table if exists %s'%tbl)
        cfg.to_sql(                     tbl,sys_eng,index=False)
        return cfg

    def adjust_settings(self,*vars):
        """
                                        '/home/ub3/SERVER4/aprinto'
        Aprinto:                        'aprinto_settings.py'
            BEHAVE_TXT_ON_ERROR
            CELERY_TXT_NOTICE
            FWD_ORDER

                                        '/home/jail/home/serv/system_config/SERVER5/celery/git_serv'
        GitServ                         'git_serv_settings.py'
            GITSERV_TXT_NOTICE
            GITSERV_GROWL_NOTICE
            BEHAVE_VERIFICATION


        BINARY USAGE:

            ... System_Control.py settings aprinto behave_txt_false

            ... System_Control.py settings nginx access_log_disable




        """

        if vars[0]=='restore':
            assert len(vars)==2
            return self.restore_orig_settings(vars[1])

        prog                        =   vars[0]
        D                           =   self.D
        binary_toggles              =   [ ['true','false'],
                                          ['enable','disable'] ]

        settings_dir                =   D[ prog ][0] % os_environ
        settings_file               =   D[ prog ][1] % os_environ
        t                           =   vars[1]
        toggle                      =   t[t.rfind('_')+1:].lower()
        param                       =   t[:-len(toggle)-1].upper()

        toggle_from,toggle_to       =   '',''
        for it in binary_toggles:
            stop                    =   False
            if it.count(toggle)==1:
                toggle_to           =   it[ it.index(toggle) ]
                toggle_from         =   it[0] if it.index(toggle)==1 else it[1]
                stop                =   True
                break

        # TO CHANGE NON-BINARY SETTINGS ... if (toggle_from,toggle_to)==('',''): ...

        delim                       =   None if ['nginx','hosts'].count(prog)==1 else '='
        cfg_file                    =   settings_dir + '/' + settings_file

        cfgs                        =   self.get_config_params(cfg_file,param,
                                                               delim=delim,
                                                               toggle_from=toggle_from)

        cfgs                        =   self.change_config_params(prog,cfg_file,cfgs,toggle_from,toggle_to)

        updated                     =   self.update_program_with_settings(prog)
        assert updated==True

        return cfgs

    def restore_settings(self,cfgs):

        # not sure this double eval is necessary BUT IT IS !!
        cfgs                        =   cfgs if type(cfgs)==list else eval(cfgs)
        cfgs                        =   cfgs if type(cfgs)==list else eval(cfgs)

        progs                       =   []
        for d in cfgs:

            d.update(                   {'from'                 :   d['to'],
                                         'to'                   :   d['from'] } )

            cmd                     =   'sed -i \'%(line)ss/%(from)s/%(to)s/g\' %(fpath)s' % d
            cmd                     =   cmd if os_access(d['fpath'],os_X_OK) else self.auth % {'cmd':cmd}
            p                       =   sub_popen(cmd,stdout=sub_PIPE,shell=True)
            (_out,_err)             =   p.communicate()
            assert _err==None
            if progs.count(d['prog'])==0:
                progs.append(           d['prog'])

        for prog in progs:
            updated                     =   self.update_program_with_settings(prog)
            assert updated==True

    def get_config_params(self,cfg_file,cfg_params,delim=None,toggle_from=''):
        mod                         =   '#' if toggle_from=='disable' else ''
        param_value                 =   toggle_from if ['enable','disable'].count(toggle_from)==0 else ''
        D                           =   {'fpath'                :   cfg_file,
                                         'mod'                  :   mod,
                                         'param_val'            :   param_value}
        cfg_params                  =   cfg_params if type(cfg_params)==list else [cfg_params]
        cfgs                        =   []

        for it in cfg_params:
            D.update(                   {'param'                :   it} )
            cmd                     =   'cat %(fpath)s | grep -i -E -n \'^[[:space:]]*%(mod)s%(param)s.*%(param_val)s\';' % D

            p                       =   sub_popen(cmd,stdout=sub_PIPE,shell=True)
            (_out,_err)             =   p.communicate()
            assert _err==None

            for it in _out.split('\n'):
                line                =   it[:it.find(':')]
                it                  =   it[it.find(':')+1:]
                t                   =   it.split() if not delim else it.split(delim)
                m                   =   ' ' if not delim else delim

                if len(t)>=2:
                    cfgs.append(        {'line'                 :   line,
                                         'param'                :   t[0].strip(),
                                         'value'                :   '%s'%m.join(t[1:]).lstrip(' %s' % m) })

        return cfgs

    def change_config_params(self,prog,cfg_file,cfg_params,toggle_from,toggle_to):
        for d in cfg_params:

            t_from,t_to             =   d['value'],toggle_to

            if ['enable','disable'].count(toggle_from)>0:
                t_from,t_to         =   d['param'],d['param']
                t_to                =   t_to.lstrip('#') if toggle_to=='enable' else t_to
                t_to                =   '#' + t_from if toggle_to=='disable' else t_to

            t_to                    =   t_to.lower() if t_from.islower() else t_to
            t_to                    =   t_to.title() if t_from.istitle() else t_to
            t_to                    =   t_to.upper() if t_from.isupper() else t_to

            d.update(                   {'prog'                 :   prog,
                                         'fpath'                :   cfg_file,
                                         'from'                 :   t_from,
                                         'to'                   :   t_to } )


            cmd                     =   'sed -i \'%(line)ss/%(from)s/%(to)s/g\' %(fpath)s' % d
            cmd                     =   cmd if os_access(cfg_file,os_X_OK) else self.auth % {'cmd':cmd}
            p                       =   sub_popen(cmd,stdout=sub_PIPE,shell=True)
            (_out,_err)             =   p.communicate()
            assert _err==None

        return cfg_params

    def update_program_with_settings(self,prog):
        if len(self.D[prog])==3:
            cmd                     =   self.D[prog][2] % os_environ
            p                       =   sub_popen(cmd,stdout=sub_PIPE,shell=True)
            (_out,_err)             =   p.communicate()
            assert _err==None
        return True

class System_Crons:
    """Cron functions to operate"""

    def __init__(self,_parent=None):
        self.T                              =   System_Lib().T if (not hasattr(self,'T') and not _parent) \
                                                    else _parent.T if not hasattr(self,'T') else self.T
        locals().update(                        self.T.__dict__)
        from crontab                        import CronTab
        from crontab                        import CronItem as type_cron
        SERVERS                             =   System_Servers(self)
        S                                   =   SERVERS.servers
        S                                   =   S[S.server_idx.isnull()==False].copy()
        S['SERV_dir']                       =   S.ix[:,['home_dir','server_idx']].apply(lambda s: s[0]+'/SERVER'+str(int(s[1])),axis=1)
        self.servers                        =   S
        self.worker                         =   SERVERS.worker
        self.Reporter                       =   System_Reporter(self)
        self.crons                          =   pd.read_sql('select * from crons',sys_eng)
        all_imports                         =   locals().keys()
        for k in all_imports:
            self.T.update(                          {k              :   eval(k) })
        T                                   =   self.T
        locals().update(                        T.__dict__)
        globals().update(                       T.__dict__)

    def osx_env(self):
        shell                       =   '/bin/bash'
        path                        =   """
            /opt/local/bin:/opt/local/sbin:/opt/local/include:/opt/local/lib:
            /usr/local/bin:/usr/local/sbin:/usr/local/include:/usr/local/lib:
            /usr/bin:/usr/sbin:
            /bin                        """.replace('\n','').replace(' ','')
        mailto                      =   '6174295700@vtext.com'
        environment_var             =   "SHELL=%s\nPATH=%s\nMAILTO=%s" % (shell,path,mailto)
        return environment_var
    def ubuntu_env(self,logname,home_dir):
        shell                       =   '/bin/bash'
        path                        =   """
            /usr/local/bin:/usr/local/sbin:/usr/local/include:/usr/local/lib:
            /usr/bin:/usr/sbin:
            /bin                        """.replace('\n','').replace(' ','')
        mailto                      =   '6174295700@vtext.com'
        environment_var             =   "SHELL=%s\nPATH=%s\nHOME=%s\nLOGNAME=%s\nMAILTO=%s"%(shell,path,home_dir,logname,mailto)
        return environment_var
    def update_cron_json(self,current_server,target_server,cron_info,cron_json):
        cron_id                     =   str(self.T.get_guid())
        
        cron                        =   self.T.CronTab()
        cron.lines                  =   []
        if target_server.tag==current_server.tag:
            crontab_copy            =   'cp -R /tmp/crontab %s/crons/' % target_server.SERV_dir
        else:
            crontab_copy            =   "ssh %s 'scp %s:/tmp/crontab $SERV_HOME/crons/'" % (target_server,current_server)


        # Create Crontab File
        cmd                         =   cron_info.cmd % target_server
        # (move cmd inside bash script)
        cmd                         =   cmd.replace("'","\'")
        cmd                         =   "./cron_script '" + cmd + "'"
        
        cmt                         =   cron_info.tag
        j                           =   cron.new(command=cmd,comment=cmt)

        if type(cron_info.special) ==   self.T.NoneType:
            t                       =   cron_info
            run_time                =   (t.minute,t.hour,t.day_of_month,t.month,t.day_of_week)
            j.setall(                   '%s %s %s %s %s'%run_time)
        else:
            s                       =   cron_info.special
            if   s == '@reboot':        j.every_reboot()
            elif s == '@hourly':        j.every().hours()
            elif s == '@daily':         j.every().dom()
            elif s == '@weekly':        j.setall('0 0 * * 0')
            elif s == '@monthly':       j.every().month()
            elif s == '@yearly':        j.every().year()
            elif s == '@annually':      j.every().year()
            elif s == '@midnight':      j.setall('0 0 * * *')
        
        # Add Environment Vars
        if target_server.tag.find('ub')==0:  
            e_v                             =   self.ubuntu_env(current_server.tag,
                                                                target_server.home_dir)
        else:                   
            e_v                             =   self.osx_env()
        
        crontab_load                        =   "ssh %s 'crontab %s/crons/crontab'"%(current_server.tag,
                                                                                     target_server.SERV_dir)
        
        if not cron_json.has_key(target_server.tag):
            cron_json.update({                  target_server.tag           :   {}      })
            
        cron_json[target_server.tag].update(    {cron_id                    :   {'cron'             :   str(j.cron),
                                                                                 'cron_env'         :   e_v,
                                                                                 'crontab_copy'     :   crontab_copy,
                                                                                 'crontab_load'     :   crontab_load}
                                                })
        
        return cron_json
    def load_crons_from_json(self,cron_json):
        for grp_k,grp_v in cron_json.iteritems():
            cron                            =   CronTab()
            cron.lines                      =   []

            for k,v in grp_v.iteritems():
                cron.lines.append(              v['cron'].strip('\n'))
                cron_env                    =   v['cron_env']
                crontab_copy                =   v['crontab_copy']
                crontab_load                =   v['crontab_load']

            # Add Environmental Vars
            tmp                             =   cron_env.split('\n')
            tmp.reverse(                        )
            cron.lines.insert(                  0,'')
            for it in tmp:
                cron.lines.insert(              0,it)
            
            # Write cron to local tmp file
            with open('/tmp/crontab','w') as f: f.write('')
            cron.write(                 '/tmp/crontab')

            
            # Copy & Load Crontab File
            if grp_k == SERVERS.worker:
                proc                        =   self.T.sub_check_output(crontab_copy, shell=True)
                cron.write_to_user()
            else:
                cmds                        =   ['scp -r %s:/tmp/crontab /tmp/ 2>&1;' % (SERVERS.worker),
                                                 'crontab /tmp/crontab || exit 1;',
                                                 'rm -fr /tmp/crontab;']
                (_out,_err)                 =   self.T.exec_cmds({'cmds':cmds,'cmd_host':grp_k,'cmd_worker':SERVERS.worker})
                assert          _out       ==   ''
                assert          _err        is  None
                cmds                        =   ['rm -fr /tmp/crontab;']
                (_out,_err)                 =   self.T.exec_cmds({'cmds':cmds})
        return
    
    @arg('target',nargs='+',default=os_environ['USER'],choices=parse_choices_from_pgsql("""
                                                                select distinct server res
                                                                from servers
                                                                where server_idx is not null
                                                                order by server
                                                             """) + ['ALL'],
        help='target server on which to change cron settings')
    @arg('-R','--results',nargs='*',
         default=['log'],
         choices                            =   [name.lstrip('_') for name,fx
                                                in inspect.getmembers(System_Reporter,inspect.ismethod)
                                                if (name.find('_')==0 and name.find('__')==-1)],
         help='options for handling RESULTS')
    @arg('-E','--errors',nargs='*',
         default=['paste','log','txt'],
         choices                            =   [name.lstrip('_') for name,fx
                                                in inspect.getmembers(System_Reporter,inspect.ismethod)
                                                if (name.find('_')==0 and name.find('__')==-1)],
         help='options for handling ERRORS (Note: No reporting if only ERRORS are defined and no error output)')
    def load(self,args):
        """Load all crons in target server(s)"""

        cron_list                           =   self.T.pd.read_sql("""  select * from crons
                                                                        where is_active is true
                                                                   """, self.T.sys_eng)
        target_servs                        =   args.target if not args.target==['ALL'] else sorted(self.T.S.tag.unique().tolist())
        current_server                      =   self.T.S[self.T.S.tag==self.T.THIS_PC].iloc[0,:]
        for _serv in target_servs:
            serv_cron_list                  =   cron_list[cron_list.server.str.contains(_serv)]
            if not len(serv_cron_list):
                pass
            else:
                target                      =   self.T.S[self.T.S.tag==_serv].iloc[0,:]
                cron_json                   =   {}
                for idx,cron in serv_cron_list.iterrows():
                    cron_json               =   self.update_cron_json(current_server,target,cron,cron_json)
                self.load_crons_from_json(      {_serv                  :       cron_json[_serv]} )
        return

    
    @arg('cron',nargs='?',choices=parse_choices_from_pgsql( """
                                                            select distinct tag res
                                                            from crons
                                                            where not is_active is false
                                                            """),
        help='cron tag to disable')
    def disable(self,args):
        """Disable a specific cron on one, several, or all servers (feat. under devel.)"""
        self.T.conn.set_isolation_level( 0)
        self.T.cur.execute(              "update crons set is_active = false where tag = '%s';" % args.cron)    
        self.list(                      args.cron)

    @arg('cron',nargs='?',choices=parse_choices_from_pgsql( """
                                                            select distinct tag res
                                                            from crons
                                                            where is_active is false
                                                            """),
        help='cron tag to enable')
    def enable(self,args):
        """Enable a specific cron on one, several, or all servers (feat. under devel.)"""
        self.T.conn.set_isolation_level( 0)
        self.T.cur.execute(              "update crons set is_active = true where tag = '%s';" % args.cron)
        self.list(                      args.cron)

    @arg()
    def list(self,args):
        print self.T.pd.read_sql("select * from crons order by is_active,tag",self.T.sys_eng)


    @arg('-R','--results',nargs='*',
         default=['log'],
         choices                            =   [name.lstrip('_') for name,fx
                                                in inspect.getmembers(System_Reporter,inspect.ismethod)
                                                if (name.find('_')==0 and name.find('__')==-1)],
         help='options for handling RESULTS')
    @arg('-E','--errors',nargs='*',
         default=['paste','log','txt'],
         choices                            =   [name.lstrip('_') for name,fx
                                                in inspect.getmembers(System_Reporter,inspect.ismethod)
                                                if (name.find('_')==0 and name.find('__')==-1)],
         help='options for handling ERRORS (Note: No reporting if only ERRORS are defined and no error output)')
    def check_logrotate(self,args):
        """Test for checking whether logrotate is working on THIS server"""
        self.process                        =   'check_logrotate'
        self.process_start                  =   self.T.dt.now()
        self.process_params                 =   {}
        self.process_stout                  =   []
        self.process_sterr                  =   None

        (_out,_err)                         =   System_Admin().exec_cmds({'cmds':['cat /etc/logrotate.d/sv_syslog'],'cmd_host':self.worker,'cmd_worker':self.worker})
        assert _err                        is   None
        rotate_period                       =   7

        cmds                                =   ['cat /var/lib/logrotate/status | grep syslogs | grep -v \'tmp_\'']
        (_out,_err)                         =   System_Admin().exec_cmds({'cmds':cmds,'cmd_host':self.worker,'cmd_worker':self.worker})
        assert _err                        is   None
        today                               =   dt.now()
        report_failure                      =   False
        for it in _out.split('\n'):
            if it!='':
                t                           =   it.split()[1]
                z                           =   t[:t.rfind('-')]
                cron_d                      =   dt.strptime(z,'%Y-%m-%d')
                y                           =   cron_d-today
                days_since                  =   abs(y.days)
                if days_since>rotate_period:
                    report_failure          =   True

        self.process_end                    =   dt.now()
        if report_failure:
            self.process_stout.append(          'LogRotate does not appear to be working on %s' % self.worker )
            results_and_errors              =   ['_'.join(['errors'] + args.errors)]     # default -> ['errors_paste_log_txt']
        else:
            self.process_stout.append(          'LogRotate looks good on %s' % self.worker )
            results_and_errors              =   ['_'.join(['results'] + args.results)]   # default -> ['results_log']

        return self.Reporter.manage(            self,results_and_errors=results_and_errors)


    @arg('-R','--results',nargs='*',
         default=['log'],
         choices                            =   [name.lstrip('_') for name,fx
                                                in inspect.getmembers(System_Reporter,inspect.ismethod)
                                                if (name.find('_')==0 and name.find('__')==-1)],
         help='options for handling RESULTS')
    @arg('-E','--errors',nargs='*',
         default=['paste','log','txt'],
         choices                            =   [name.lstrip('_') for name,fx
                                                in inspect.getmembers(System_Reporter,inspect.ismethod)
                                                if (name.find('_')==0 and name.find('__')==-1)],
         help='options for handling ERRORS (Note: No reporting if only ERRORS are defined and no error output)')
    def find_new_pip_libs(self,args):
        """Finds new pip libs on all servers"""

        self.process                        =   'find_new_pip_libs'
        self.process_start                  =   self.T.dt.now()
        SERVS                               =   self.servers[(self.servers.server_idx>0)&(self.servers.server!='serv')].server.tolist()
        # serv excluded because redundant and sudo command difficult
        self.process_params                 =   {'SERVS'             :   SERVS }
        self.process_stout                  =   []
        self.process_sterr                  =   []
        for serv in SERVS:
            (_out,_err)                     =   exec_cmds({'cmds':['sudo /usr/bin/updatedb > /dev/null 2>&1'],'cmd_host':serv,'cmd_worker':self.worker})
            cmds                            =   ['echo $HOME;',
                                                 'a=$(which grep);',
                                                 'locate /ENV | env $a --color=never -E \'/ENV$\'']
            (_out,_err)                     =   exec_cmds({'cmds':cmds,'cmd_host':serv,'cmd_worker':self.worker})
            if not _err is None:                self.process_sterr.append(_err)
            serv_home                       =   _out.split('\n')[0]
            found_lib_locs                  =   [ it for it in _out.split('\n')[1:] if it.count(serv_home)>0 and it.count('/ENV')==1 ]
            saved_libs                      =   self.servers[self.servers.tag==serv].pip_libs.tolist()[0]

            if not saved_libs:
                to_save_locs                =  []
            else:
                known_lib_locs              =   [ saved_libs[it]['location'] for it in saved_libs.keys() ]
                new_lib_locs                =   [ it for it in found_lib_locs if known_lib_locs.count(it)==0 ]
                if not hasattr(self,'ignore_lib_D'):
                    self.health             =   System_Status()
                    self.ignore_lib_D       =   dict(zip(self.health.ignore.param2.tolist(),
                                                    self.health.ignore.server_tag.tolist()))
                to_save_locs                =   [ it for it in new_lib_locs if (self.ignore_lib_D.has_key(it)==False and it!='') ]


            if to_save_locs:

                # update dict from DB
                lib_names                   =   []
                for it in to_save_locs:
                    lib_name                =   it[it.rstrip('/ENV').rfind('/')+1:].rstrip('/ENV')
                    pt                      =   1
                    while saved_libs.keys().count(lib_name)>0:
                        if saved_libs.keys().count(lib_name+'_'+str(pt))==0:
                            lib_name        =   lib_name+'_'+str(pt)
                        else:   pt         +=   1
                    lib_names.append(           lib_name)
                    lib_info                =   {lib_name               :   { 'requirements':'','location':it }   }
                    saved_libs.update(          lib_info)
                    self.process_stout.append(  ['new_pip_lib',serv,lib_name,it])

                # update DB with updated dict
                conn.set_isolation_level(       0)
                f_saved_libs                =   self.T.j_dump(saved_libs)
                cmd                         =   """ update servers set pip_libs='%s' where tag='%s' """ % (f_saved_libs,serv)
                cur.execute(                    cmd)

                # Run backup_pip to save lib reqs to paste
                if not hasattr(self,'SYS'):
                    self.Backup             =   System_Backup(self)
                vars                        =   [serv] + lib_names
                self.Backup.pip(                *vars )

        self.process_end                    =   self.T.dt.now()
        if not self.process_sterr:
            results_and_errors              =   ['_'.join(['results'] + args.results)]   # default -> ['results_log']
        else:
            results_and_errors              =   ['_'.join(['errors'] + args.errors)]     # default -> ['errors_paste_log_txt']

        return self.Reporter.manage(            self,results_and_errors=results_and_errors)

    @arg('-R','--results',nargs='*',
         default=['log'],
         choices                            =   [name.lstrip('_') for name,fx
                                                in inspect.getmembers(System_Reporter,inspect.ismethod)
                                                if (name.find('_')==0 and name.find('__')==-1)],
         help='options for handling RESULTS')
    @arg('-E','--errors',nargs='*',
         default=['paste','log','txt'],
         choices                            =   [name.lstrip('_') for name,fx
                                                in inspect.getmembers(System_Reporter,inspect.ismethod)
                                                if (name.find('_')==0 and name.find('__')==-1)],
         help='options for handling ERRORS (Note: No reporting if only ERRORS are defined and no error output)')
    def run_git_fsck(self,args):
        """Runs `git fsck` on all master and sub repos"""
        self.process                        =   'git_fsck'
        self.process_start                  =   self.T.dt.now()
        self.process_params                 =   {}
        self.process_stout                  =   []
        self.process_sterr                  =   []
        g                                   =   self.T.pd.read_sql('select * from servers where git_tag is not null',sys_eng)
        sub_srcs,sub_dest                   =   g.git_sub_src.tolist(),g.git_sub_dest.tolist()
        master_src                          =   g.git_master_src.tolist()
        all_repos                           =   sub_srcs + sub_dest + master_src
        all_repos                           =   sorted(dict(zip(all_repos,range(len(all_repos)))).keys())
        serv                                =   '0'
        for it in all_repos:
            if it.find(serv)!=0:
                serv                        =   it[it.find('@')+1:it.rfind(':')]
            s_path                          =   it[it.rfind(':')+1:]
            cmds                            =   ['cd %s;' % s_path,
                                                 'git fsck 2>&1;']
            (_out,_err)                     =   System_Admin().exec_cmds({'cmds':cmds,'cmd_host':serv,'cmd_worker':self.worker})
            assert _err==None
            if _out!='':
                T                           =   { 'msg'                 :   'Repo needs work >>%s<<' % it,
                                                  'stdout'              :   _out}
                self.process_sterr.append(      T )

        self.process_end                    =   self.T.dt.now()
        if not self.process_sterr:
            self.process_stout.append(          'git_fsck indicates all repos look good' )
            results_and_errors              =   ['_'.join(['results'] + args.results)]   # default -> ['results_log']
        else:
            results_and_errors              =   ['_'.join(['errors'] + args.errors)]     # default -> ['errors_paste_log_txt']

        return self.Reporter.manage(            self,results_and_errors=results_and_errors)

class System_Networking:
    """Functions for managing System network"""

    def __init__(self,_parent=None):
        if not _parent:
            _parent                         =   System_Lib()
        self.T                              =   _parent.T

    @arg('-H','--host',action='append',
         choices                            =   parse_choices_from_pgsql("""
                                                    select distinct server res
                                                    from servers
                                                    where server_idx is not null
                                                    order by server
                                                 """) + ['all','ALL'],
         help='server host name')
    @arg('-p','--port',action='append',help='port(s) or port range(s)')
    @arg('-t','--tag',action='append',help='name/regex of service')
    def get(self,**args):
        """Returns [Device,Host,Service,Domain] from System pgsql with options to limit selection"""
        i_trace()
        # params                              =   ['host','port','tag']
        # d                                   =   dict(zip(params,[ args.__dict__.get(it) for it in params ]))
        # if d.values().count(None)==len(params):
        #     qry_params                      =   []
        # else:
        #     qry_params                      =   ['where']
        #     for k,v in d.iteritems():
        #         if v=='host':
        #             qry_params.append(          '_%s && array%s, and'%(k,v))
        #         elif v=='port':
        #             qry_params.append(          '_%s && array%s, and'%(k,v))
        #         elif v=='tag':
        #             qry_params.append(          '_%s && array%s, and'%(k,v))
        #     qry_params[-1]                  =   qry_params[-1][:-len(', and')]
        qry_params                      =   []
        df                                  =   self.T.pd.read_sql("select * from services %s" %
                                                                        ' '.join(qry_params),
                                                                   self.T.sys_eng)

        sort_params                         =   ['col','direction']
        return df

    @arg('port',help='port to map')
    @arg('tag',help='descriptive tag for labeling service using port')
    @arg('-H','--host',default='ALL',nargs='+',
         choices                            =   parse_choices_from_pgsql("""
                                                    select distinct server res
                                                    from servers
                                                    where server_idx is not null
                                                    order by server
                                                 """) + ['ALL'],
         help='server host name(s) for port endpoint(s)')
    def set(self,args):
        """Sets any values [Device,Host,Service,Domain] to System pgsql and updates iptables"""
        def update_pgsql():
            self.T.conn.set_isolation_level(        0)
            self.T.cur.execute(                     'DROP TABLE IF EXISTS %(tmp_tbl)s;' % self.T)
            self.results.to_sql(                    self.T['tmp_tbl'],self.T.eng)

            upd_set                             =   ','.join(['%s = t.%s' % (it,it) for it in self.results.columns])
            ins_cols                            =   ','.join(self.results.columns)
            sel_cols                            =   ','.join(['t.%s' % it for it in self.results.columns])

            self.T.update(                          {'upd_set'              :   upd_set,
                                                     'ins_cols'             :   ins_cols,
                                                     'sel_cols'             :   sel_cols,})
            # upsert to properties
            cmd                                 =   """
                                                    with upd as (
                                                        update properties p
                                                        set
                                                            %(upd_set)s
                                                        from %(tmp_tbl)s t
                                                        where p._property_id     =   t._property_id
                                                        returning t._property_id _property_id
                                                    )
                                                    insert into properties ( %(ins_cols)s )
                                                    select
                                                        %(sel_cols)s
                                                    from
                                                        %(tmp_tbl)s t,
                                                        (select array_agg(f._property_id) upd_property_ids from upd f) as f1
                                                    where (not upd_property_ids && array[t._property_id]
                                                        or upd_property_ids is null);

                                                    DROP TABLE %(tmp_tbl)s;
                                                    """ % self.T
            self.T.conn.set_isolation_level(        0)
            self.T.cur.execute(                     cmd)
        def update_router():
            nat_tbl                         =   'iptables -t nat'
            pre_routing                     =   '%s -A PREROUTING' % nat_tbl
            cmds                            =   ['#!/bin/sh',
                                                 '%s -F' % nat_tbl,
                                                 '%s -X' % nat_tbl,
                                                 '%s-Z' % nat_tbl,
                                                 '%s -p tcp -d 10.0.1.1 --dport 8080 -j REDIRECT --to-port 80' % pre_routing,
                                                 '%s -p tcp -d $(nvram get wan_ipaddr) --dport 22 -j DNAT --to $(nvram get lan_ipaddr):22' % pre_routing,
                                                 '%s -p tcp -d $(nvram get wan_ipaddr) --dport 23 -j DNAT --to $(nvram get lan_ipaddr):23' % pre_routing,
                                                 '%s -p tcp -d $(nvram get wan_ipaddr) --dport 80 -j DNAT --to 10.0.1.52:80' % pre_routing,
                                                 '%s -d $(nvram get wan_ipaddr) -j DNAT --to $(nvram get lan_ipaddr)' % pre_routing,]


        i_trace()


    def update_porting(self):

        pass

class System_Databases:

    def __init__(self):
        self.T                      =   System_Lib().T
        self.databases              =   self.T.pd.read_sql('select * from databases where is_active is True',sys_eng)

    class Tables:

        def __init__(self,_parent):
            self.T                      =   _parent.T
            self.Create                 =   self.Create(self)

        class Create:

            def __init__(self,_parent):
                self.T                  =   _parent.T
                self.Create             =   self

            def config_rsync(self):
                t = """
                    CREATE TABLE config_rsync
                    (
                        consider text,
                        include text,
                        exclude text,
                        "1.0" text,
                        "2.0" text,
                        "3.0" text,
                        "4.0" text,
                        "5.0" text,
                        "6.0" text,
                        "7.0" text,
                        "8.0" text,
                        "9.0" text,
                        "10.0" text,
                        "11.0" text,
                        "12.0" text,
                        "unnamed: 15" text,
                        prep_scripts text,
                        source_5 text,
                        functions text,
                        uid integer NOT NULL,
                        last_updated timestamp with time zone,
                        CONSTRAINT config_rsync_pkey PRIMARY KEY (uid)
                    );
                """
                pass

            def crons(self):
                t = """
                    CREATE TABLE crons
                    (
                        tag text,
                        server text,
                        minute text,
                        hour text,
                        day_of_month text,
                        month text,
                        day_of_week text,
                        uid integer NOT NULL DEFAULT z_next_free('crons'::text, 'uid'::text, 'crons_uid_seq'::text),
                        special text,
                        cmd text,
                        is_active boolean,
                        last_updated timestamp with time zone,
                        CONSTRAINT crons_pkey PRIMARY KEY (uid)
                    );
                """

            def databases(self):
                t = """
                    CREATE TABLE databases
                    (
                        db_name text,
                        db_server text,
                        backup_cmd text,
                        backup_path text,
                        is_active boolean,
                        last_updated timestamp with time zone,
                        uid integer NOT NULL,
                        CONSTRAINT databases_pkey PRIMARY KEY (uid)
                    );
                """

            def servers(self):
                t = """
                    CREATE TABLE servers
                    (
                        id serial NOT NULL,
                        tag text,
                        web_service text,
                        domain text,
                        local_addr text,
                        local_port integer,
                        server text,
                        home_dir text,
                        subdomain_dest text,
                        production_usage text,
                        server_idx integer,
                        mac bigint,
                        remote_addr text,
                        is_active boolean,
                        subdomain text,
                        dns_ip text,
                        socket text,
                        remote_port integer,
                        model_id text,
                        serial_id text,
                        last_updated timestamp with time zone,
                        git_sub_src text,
                        git_sub_dest text,
                        git_master_src text,
                        git_master_dest text,
                        pip_libs json,
                        pip_last_updated timestamp with time zone,
                        git_tag text,
                        host text,
                        mnt_up text[],
                        mnt_dev text[],
                        CONSTRAINT servers_pkey PRIMARY KEY (id)
                    );
                """

            def shares(self):
                t = """
                    CREATE TABLE shares
                    (
                        remote_path text,
                        tag text,
                        last_updated timestamp with time zone,
                        uid integer NOT NULL,
                        CONSTRAINT tmp_pkey PRIMARY KEY (uid)
                    );
                """

            def system_health(self):
                t = """
                    CREATE TABLE system_health
                    (
                        type_tag text,
                        server_tag text,
                        param1 text,
                        param2 text,
                        last_updated timestamp with time zone,
                        uid integer NOT NULL,
                        CONSTRAINT system_health_pkey PRIMARY KEY (uid)
                    );
                """

            def system_log(self):
                t = """
                    CREATE TABLE system_log
                    (
                        operation text,
                        started timestamp with time zone,
                        parameters text,
                        stout text,
                        sterr text,
                        ended timestamp with time zone,
                        uid integer NOT NULL,
                        last_updated timestamp with time zone,
                        CONSTRAINT system_log_pkey PRIMARY KEY (uid)
                    );
                """

            def gmail(self):
                t = """
                    CREATE TABLE gmail
                    (
                        orig_msg jsonb,
                        gmail_id bigint,
                        msg_id text
                    );
                """
                self.T.conn.set_isolation_level(0)
                self.T.cur.execute(t)

class System_Servers:
    """Functions for Mounting & Unmounting system drives"""

    def __init__(self,_parent=None):
        self.T                              =   System_Lib().T if (not hasattr(self,'T') and not _parent) \
                                                    else _parent.T if not hasattr(self,'T') else self.T
        locals().update(                        self.T.__dict__)
        shares                              =   self.T.pd.read_sql('select * from shares',self.T.sys_eng)
        s                                   =   self.T.pd.read_sql('select * from servers where production_usage is not null',self.T.sys_eng)
        self.sh         =   self.shares     =   shares
        self.s          =   self.servers    =   s
        server_dir_dict                     =   dict(zip(s.tag.tolist(),s.home_dir.tolist()))
        mac                                 =   [int(str(get_mac()))]
        worker                              =   s[ s.mac.isin(mac) & s.home_dir.isin([os_environ['HOME']]) ].iloc[0].to_dict()
        self.worker                         =   worker['server']
        self.worker_host                    =   worker['host']
        global THIS_SERVER
        THIS_SERVER                         =   self.worker
        self.base_dir                       =   worker['home_dir']
        self.server_idx                     =   worker['server_idx']
        rank                                =   {'high':3,'medium':2,'low':1,'none':0}
        s['ranking']                        =   s.production_usage.map(rank)
        self.priority                       =   dict(zip(s.tag.tolist(),s.ranking.tolist()))
        self.mgr                            =   self
        all_imports                         =   locals().keys()
        
        excludes                            =   ['D','self']
        for k in all_imports:
            if not excludes.count(k):
                self.T.update(                  {k                          :   eval(k) })
        
        globals().update(                       self.T.__dict__)

    @arg('mnt_src',nargs='?',help="SSH source, e.g., admin@localhost:1234:/home/admin/foo (see 'bind_address' in `man ssh`)")
    @arg('mnt_as_vol',nargs='?',default='',help='name of mount point dir in \'/Volumes\'')
    def mnt_sshfs(self,mnt_src,mnt_as_vol):
        """mount ssh source to this server in dir '/Volumes'"""

        sshfs                       =   self.T.os_environ['SSHFS']+' '

        cmds                        =   ['sudo umount -f %s > /dev/null 2>&1;' % mnt_as_vol]
        (_out,_err)                 =   self.T.exec_cmds({'cmds':cmds})

        cmds                        =   ['mkdir -p %s;' % mnt_as_vol,
                                         '%s %s %s -o ConnectTimeout=5 2>&1;' % (sshfs,mnt_src,mnt_as_vol),]

        err                         =   False
        try:
            (_out,_err)             =   self.T.exec_cmds({'cmds':cmds})
            if _out.count('Connection reset'):
                err                 =   True
        except:
            err                     =   True

        if err:
            t                       =   mnt_as_vol.split('/')[-1]
            serv_is_low_prod_use    =   len(self.s[ (self.s.tag==t) &
                                                    (self.s.production_usage=='low') ] )
            if not serv_is_low_prod_use:
                i_trace()
                print                   mnt_src,'mount failed'
            (_out,_err)             =   self.T.exec_cmds({'cmds':['rm -fR %s ; ' % mnt_as_vol]})
            assert _err            is   None

        return

    @arg('shares',nargs='+',default='',choices=parse_choices_from_pgsql("""
            select _res res
            from (
                select distinct unnest(res) _res
                from (

                    select string_to_array(concat(a,','::text,b),','::text) res 
                    from (
                        select * from
                        (select array_to_string(array_agg(distinct tag),','::text) a from shares) shares,
                        (select array_to_string(array_agg(tag),','::text) b from servers where server_idx is not null) servers
                    ) f
                ) f2
            ) f3
            order by _res asc """)+['DEV','ALL','_'],
            help='target server on which to backup pip')
    def mnt(self,shares=[]):
        """mount known shares to this server at '/Volumes/{SHARE}'"""

        shares                              =   shares.shares if shares.__class__.__module__=='argparse' else shares

        # Compensate for short-hand references to servers, i.e., 'ub1' for 'SERVER1'
        # servs                               =   self.s[self.s.server_idx.isnull()==False].ix[:,['tag','server_idx']]
        # serv_dict                           =   dict(zip(servs.tag.tolist(),
        #                                                  servs.server_idx.map(lambda t: 'SERVER'+str(int(t))) ))
        # shares                              =   map(lambda t: t if not serv_dict.has_key(t) else serv_dict[t],shares)

        if not shares or shares[:]==['_']:
            shares                          =   map(lambda s: str(s.strip("'")),
                                                self.s[self.s.tag==self.worker].mnt_up.tolist()[:][0] )
            shares_D                        =   dict(zip([ '/Volumes/' + it for it in shares ],
                                                         [ '%s:/' % it for it in shares ]))
        elif shares[:].count('DEV'):
            shares                          =   map(lambda s: str(s.strip("'")),
                                                    self.s[self.s.tag==self.worker].mnt_dev.tolist()[:][0] )
            shares_D                        =   dict(zip([ '/Volumes/' + it for it in shares ],
                                                         [ '%s:/' % it for it in shares ]))

        elif shares[:].count('ALL'):
            new_shares                      =   self.sh[self.sh.remote_path.str.contains(self.worker)==False]
            shares_D                        =   dict(zip(new_shares.tag.tolist(),new_shares.remote_path.tolist()))

        else:
            mnt_srcs                        =   map(lambda it: '%s:/' % it if not self.sh[self.sh.tag==it].remote_path.tolist() 
                                                    else self.sh[self.sh.tag==it].remote_path.tolist()[0],shares)
            shares_D                        =   dict(zip([ '/Volumes/' + it for it in shares ],
                                                 mnt_srcs))

        (_out,_err)                         =   self.T.exec_cmds({'cmds':'ps -axww'})
        assert _err                        is   None

        for mnt_as_vol,mnt_src in shares_D.iteritems():
            if not re_findall(mnt_as_vol,_out):
                self.mnt_sshfs(                 mnt_src,mnt_as_vol)

        return

    @arg('shares',nargs='+',default='',choices=parse_choices_from_exec("""
                                                                    echo `ls /Volumes`;
                                                                 """).strip('\n').split()+['ALL'],
            help='share dirs on this server')
    def umnt(self,dirs=['ALL'],local=True):
        """unmount linked source(s) from this server in dir '/Volumes'"""
        if dirs==['ALL']:
            cmds                    =   ["df 2>/dev/null | awk '/\\/Volumes\\// {print $NF}' | xargs -I{} sudo /bin/umount -f {};",
                                         "unalias ls > /dev/null 2&<1;",
                                         "ls /Volumes | xargs -I{} /bin/rmdir /Volumes/{};",]
            (_out,_err)             =   self.T.exec_cmds({'cmds':cmds})
            assert _err            is   None
            assert _out            ==   ''
        else:
            cmds                    =   []
            for it in dirs:
                cmds.extend(            ['sudo /bin/umount -f /Volumes/%s;' % it,
                                         '/bin/rmdir /Volumes/%s;' % it] )
            (_out,_err)             =   self.T.exec_cmds({'cmds':cmds})
            assert _err            is   None
            assert _out            ==   ''

class System_Status:
    """Functions for checking system statuses"""

    def __init__(self):
        self.T                      =   System_Lib().T
        locals().update(                self.T.__dict__)
        s                           =   System_Servers()
        self.servers                =   s.servers
        self.worker                 =   s.worker
        h                           =   pd.read_sql('select * from system_health',sys_eng)
        self.Reporter               =   System_Reporter(self)
        self.processes              =   h[h.type_tag=='process'].copy()
        self.mounts                 =   h[h.type_tag=='mount'].copy()
        self.checks                 =   h[h.type_tag=='check'].copy()
        self.ignore                 =   h[h.type_tag=='ignore'].copy()

    @arg('target',nargs='?',default=os_environ['USER'],choices=parse_choices_from_pgsql("""
                                                                select distinct server res
                                                                from servers
                                                                where server_idx is not null
                                                                order by server
                                                             """),
        help="server on which to check status")
    @arg('-R','--results',nargs='*',#action='append',
         default=['log'],
         choices                    =   [name.lstrip('_') for name,fx
                                         in inspect.getmembers(System_Reporter,inspect.ismethod)
                                         if (name.find('_')==0 and name.find('__')==-1)] + ['',None],
         help='options for handling RESULTS')
    @arg('-E','--errors',nargs='*',#action='append',
         default=['paste','log','txt'],
         choices                    =   [name.lstrip('_') for name,fx
                                         in inspect.getmembers(System_Reporter,inspect.ismethod)
                                         if (name.find('_')==0 and name.find('__')==-1)] + ['',None],
         help='options for handling ERRORS (Note: No reporting if only ERRORS are defined and no error output)')
    def make_display_check(self,args):
        """ Compares active processes on target server with expected processes from DB and returns pretty results. """

        self.process                        =   'System_Status_Check on %s' % args.target
        self.process_start                  =   self.T.dt.now()
        self.process_params                 =   {}
        self.process_stout                  =   []
        self.process_sterr                  =   []
        chk_sys                             =   args.target
        P                                   =   self.processes
        procs                               =   P[ P.server_tag==chk_sys ].ix[:,['param1','param2']]
        procs                               =   dict(zip(procs.param1.tolist(),procs.param2.tolist()))

        if  chk_sys                        !=   self.worker:
            t                               =   'ssh %s "ps -axww"'%chk_sys
            cmd                             =   shlex.split(t)
        else: cmd                           =   ['ps','-axww']

        p                                   =   sub_popen(cmd,stdout=sub_PIPE)
        (ap, err)                           =   p.communicate()
        res,errs,wc                         =   [],[],r'#'
        chk_templ                           =   "printf $(tput bold && tput setaf 1)\"chk\"$(tput setaf 9 && `tput rmso`)\\\\t\"%s\\\\n\";"
        ok_templ                            =   "printf $(tput bold && tput setaf 2)\"ok\"$(tput setaf 9 && `tput rmso`)\\\\t\"%s\\\\n\";"
        issue_templ                         =   'Issue on "%s" with check: "%s"'

        for k in sorted(procs.keys()):

            if len(re_findall(procs[k],ap))==0:

                res.append(                     chk_templ % k)
                errs.append(                    issue_templ % (chk_sys,k) )
            else:
                res.append(                     ok_templ % k)

        C                                   =   self.checks
        checks                              =   C[ C.server_tag==chk_sys ].ix[:,['param1','param2']]
        checks                              =   dict(zip(checks.param1.tolist(),checks.param2.tolist()))
        for k in sorted(checks.keys()):

            cmd                             =   checks[k]
            if chk_sys!=self.worker:
                cmd                         =   "ssh %s '%s'" % (chk_sys,cmd)
            p                               =   sub_popen(cmd,stdout=sub_PIPE,shell=True)
            (_out,_err)                     =   p.communicate()

            if not _out.count('1'):
                res.append(                     chk_templ % k)
                errs.append(                    issue_templ % (chk_sys,k))
            else:
                res.append(                     ok_templ % k)

        print ''.join(                          res).rstrip('\\n";') + '";'

        self.process_sterr                  =   errs if errs else None
        self.process_end                    =   self.T.dt.now()

        if not self.process_sterr and hasattr(args,'results'):
            results_and_errors              =   ['_'.join(['results'] + args.results)]   # default -> ['results_log']
            return self.Reporter.manage(        self,results_and_errors=results_and_errors)
        elif hasattr(args,'errors'):
            results_and_errors              =   ['_'.join(['errors'] + args.errors)]     # default -> ['errors_paste_log_txt']
            return self.Reporter.manage(        self,results_and_errors=results_and_errors)

        return

### --- MUST LEAVE THIS CLASS AT BOTTOM ---

### ---                      ---

if __name__ == '__main__':
    # run_custom_argparse()
    import os
    f                                       =   __file__
    THIS_MODULE                             =   os.path.dirname(os.path.abspath(f)) + f[f.rfind('/'):]
    mod_regex                               =   'System_(.*)'
    mod_excludes                            =   ['System_Lib','System_Argparse','System_Databases']

    c                                       =   parse_module(mod_path=THIS_MODULE,
                                                             regex=mod_regex,
                                                             excludes=mod_excludes)
    if not c:                                   raise SystemExit
    if type(c)==tuple:                  c   =   c[0]
    D                                       =   {}
    D.update(                                   locals())
    for k,v in D.iteritems():
        if re_findall(mod_regex,k) and inspect.isclass(v) and not mod_excludes.count(k):
            if re_sub(mod_regex,'\\1',k).lower() == c._class:
                THIS_CLASS                  =   v()
                break

    return_var                              =   getattr(THIS_CLASS,c._func)(c)
    if locals().has_key('return_var'):
        if return_var:                          print return_var





    # NEED TO ADD 'overright' and 'upgrade' to install-pip options

    # if c._func=='admin':
    #     SYS                                 =   System_Admin()
    #     getattr(SYS, c._func)(c)
    # elif c._func=='backup':
    #     i_trace()
    #     pass
    # elif c._func=='install':
    #     SYS                                 =   System_Admin()
    #     install_vars                        =   [c.pip_dest,c.install_dest,
    #                                              c.pip_src,c.pip_lib,
    #                                              c.install_opts]
    #     SYS.install_pip(                        *install_vars)
    # elif c._func=='status':
    #     SYS                                 =   System_Health()
    #     for it in c.status:
    #         SYS.make_display_check(             it)
    #
    #
    # elif c._func=='cron':
    #     SYS                                 =   System_Crons()
    #     getattr(SYS, c.cron[0])(c.cron_params)
    #
    # elif c._func=='config':
    #     pass
    #
    # elif c._func=='mnt' or c._func=='umnt':
    #     pass



    #     elif argv[1]=='cron':
    #         CRON                        =   System_Crons()
    #         if   argv[2]=='logrotate':
    #             CRON.check_log_rotate(      )
    #         elif argv[2]=='git_fsck':
    #             CRON.run_git_fsck(          )
    #         elif argv[2]=='find_new_pip_libs':
    #             CRON.find_new_pip_libs(     argv[3:])
    #         elif argv[2]=='authorize':
    #             CRON.authorize(             argv[3:])

    #     elif argv[1]=='settings':
    #         CFG                         =   System_Config()
    #         return_var                  =   CFG.adjust_settings( *argv[2:] )

    #     elif ['mnt','umnt'].count(argv[1]):
    #         SERVS                       =   System_Servers()
    #         return_var                  =   SERVS.mnt_shares(argv[2:]) if argv[1]=='mnt' else SERVS.umnt_shares(argv[2:])



    #     if argv[1].find('backup_')==0:
    #         SYS                         =   System_Admin()
    #         if (len(argv)>2 and argv[2]=='dry-run'):
    #             SYS.dry_run             =   True
    #         elif len(argv)>2:
    #             vars                    =   argv[2:]
    #         else:
    #             vars                    =   []


    #         if  argv[1]=='backup_all':
    #             SYS.backup_ipython(         )
    #             SYS.backup_databases(       )
    #             SYS.backup_system(          )
    #             SYS.backup_pip(             )


    #         elif  argv[1]=='backup_ipython':     SYS.backup_ipython()
    #         elif  argv[1]=='backup_databases':   SYS.backup_databases()
    #         elif  argv[1]=='backup_system':      SYS.backup_system()
    #         elif  argv[1]=='backup_pip':         SYS.backup_pip(*vars)

    # if return_var:                          print return_var