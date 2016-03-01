

# from IPython import embed_kernel as embed; embed()
from ipdb import set_trace as i_trace
#i_trace()

class Google:

    def __init__(self):
        self.T                      =   System_Lib().T
        # from googlevoice import Voice
        # from googlevoice.util import input
        # self.Voice                  =   Voice()
        # self.Voice.login('aporodeliveryllc@gmail.com',
        #                  '100%delivery')
        pass

    def _msg(self,phone_num,msg):
        # _out                        =   self.Voice.send_sms(phone_num, msg)
        # assert _out==None
        return

class PasteBin:
    """
    Module:                             http://pythonhosted.org/pastebin_python/code.html

    Expiration Format:                  (see http://pastebin.com/api#6)

                    Input               Description
                    'N'                 Never
                    '10M'               10 minutes
                    '1H'                1 hour
                    '1D'                1 day
                    '1W'                1 week
                    '2W'                2 weeks
                    '1M'                1 month

    Publication Format:

                    public          =   0,
                    unlisted        =   1,
                    private         =   2

    """
    def __init__(self):
        from pastebin_python            import PastebinPython
        user_name                   =   'mech_coder'
        passw                       =   'Delivery100%'
        dev_key                     =   '4f26d1cb7a08f03b02ab24dae43bc431'
        pb                          =   PastebinPython(api_dev_key=dev_key)
        pb.createAPIUserKey(            user_name,passw)
        self.pb                     =   pb

class System_Build:

    def __init__(self):
        self.T                      =   System_Lib().T
        s                           =   System_Servers()
        self.servers                =   s.servers
        self.worker                 =   s.worker
        self.params                 =   {}
        self.reporter               =   System_Reporter()
        self.pb                     =   self.reporter.pb

    def configure_scripts(self,*vars):
        if len(vars)==0: cmd_host   =   self.worker
        else:            cmd_host   =   vars[0]

        cmds                        =   ['cd $HOME/.scripts;',
                                         'if [ -n "$(cat ENV/bin/activate | grep \'source ~/.bashrc\')" ]; then',
                                         'echo -e "\nsource ~/.bashrc\n" >> ENV/bin/activate;'
                                         'fi;']
        (_out,_err)                 =   exec_cmds(cmds,cmd_host,self.worker)
        assert _err==None
        assert _out==''

class System_Reporter:
    """
    System_Reporter uniformly manages output and errors.

    Input is taken from                 self.process,
                                            .process_start,
                                            .process_params,
                                            .process_stout,
                                            .process_sterr, and
                                            .process_end


    Assuming this class has already been initiated with:

        self.reporter               =   System_Reporter()


    Usage [ e.g., at the end of a function ]:

        return self.reporter.manage(    self,results_and_errors)


    Where 'results_and_errors' is a list
        with any one or more of the options:

                                        ['','results_print','results_log','results_log_txt',
                                         'results_paste_log','results_paste_log_txt',
                                         'errors_print','errors_log','errors_log_txt',
                                         'errors_paste_log','errors_paste_log_txt']

    Note, if designations only exist for errors,
      no results are processed if self.process_sterr is empty.


    Template:

        self.process                =   ''
        self.process_start          =   dt.now()
        self.process_params         =   {}
        self.process_stout          =   []
        self.process_sterr          =   None
        self.process_end            =   dt.now()
        return self.reporter.manage(    self,results_and_errors='')

    """

    def __init__(self):
        self.T                      =   System_Lib().T
        locals().update(                self.T.__getdict__())
        s                           =   System_Servers()
        self.servers                =   s.servers
        self.worker                 =   s.worker
        self.pb                     =   PasteBin().pb
        # self.google                 =   Google()
        # self.GV                     =   self.google.Voice

    def manage(self,admin,results_and_errors):
        """

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
            grp                     =   res
        else: grp                   =   res + err

    #   2. Combine all rules into single Rule.
        t                           =   []
        for it in grp:
            t.extend(                   it.split('_') )
        methods                     =   dict(zip(t,range(len(t)))).keys()

    #   3. Create Message.
        runtime                     =   (admin.process_end-admin.process_start)
        if runtime.total_seconds()/60.0 < 1:
            runtime_txt             =   'Runtime: %s seconds' % str(runtime.total_seconds())
        else:
            runtime_txt             =   'Runtime: %s minutes' % str(runtime.total_seconds()/60.0)

        msg_title                   =   '["%s" ENDED]' % admin.process
        msg                         =   [msg_title,
                                         '',
                                         'Parameters: %s' % str(admin.process_params),
                                         '',
                                         'Started: %s' % dt.isoformat(admin.process_start),
                                         runtime_txt,
                                         '']
        msg_summary                 =   ', '.join([it for it in msg if it!=''])

        if res:
            if type(admin.process_stout)!=list:
                admin.process_stout =   [ admin.process_stout ]
            if not (len(admin.process_stout)==0 or [None,'None','',[]].count(admin.process_stout)==1):
                msg.extend(             ['Output: ',''])
                msg.extend(             admin.process_stout )
                msg.extend(             [''] )

        if err:
            if type(admin.process_sterr)!=list:
                admin.process_sterr =   [ admin.process_sterr ]
            if not (len(admin.process_sterr)==0 or [None,'None','',[]].count(admin.process_sterr)==1):
                msg.extend(             ['Errors: ',''] )
                msg.extend(             admin.process_sterr )
                msg.extend(             [''] )

        msg_str                     =   '\n'.join([str(it) for it in msg])

    #   4. Process results with Message and according to Rule.
        if methods.count('print')==1:
            self._print(                msg)

        if methods.count('paste')==1:
            pb_url                  =   self._paste(msg_title,msg_str)
            log_msg                 =   ' - '.join([ msg_summary,pb_url ])
        else:
            log_msg                 =   msg_summary

        if methods.count('txt')==1:
            self._txt(                  log_msg)

        if methods.count('log')==1:
            self._log(                  log_msg)
        # ---

    def _print(self,msg):
        for it in msg:
            print it
        return

    def _paste(self,msg_title,msg_str):
        pb_url                      =   self.pb.createPaste( msg_str,
                                            api_paste_name=msg_title,
                                            api_paste_format='',
                                            api_paste_private='1',
                                            api_paste_expire_date='1M')
        return pb_url

    def _g_txt(self,log_msg,phone_num='6174295700'):
        self.GV._msg(                   phone_num, log_msg)
        return

    def _txt(self,log_msg):
        opt                         =   'F' if os_environ['USER']=='admin' else 't'
        cmd                         =   'echo "%s" | mail -%s 6174295700@vtext.com' % (log_msg,opt)
        proc                        =   sub_popen(cmd, stdout=sub_PIPE, shell=True)
        (_out, _err)                =   proc.communicate()
        assert _out==''
        assert _err==None
        return

    def _log(self,log_msg):
        cmd                         =   'logger -t "System_Reporter" "%s"' % log_msg
        proc                        =   sub_popen(cmd, stdout=sub_PIPE, shell=True)
        (_out, _err)                =   proc.communicate()
        assert _out==''
        assert _err==None
        return

    def _growl(self,log_msg,url=''):
        if url:
            cmd                     =   'growlnotify -m "%s" --url %s' % (log_msg,url)
        else:
            cmd                     =   'growlnotify -m "%s"' % log_msg
        from ipdb import set_trace as i_trace; i_trace()
        exec_cmds(                      [cmd],'mbp2',self.worker)

class System_Config:

    def __init__(self):
        """

            Entry Format: [ {settings directory},{settings file},{cmd to reset program settings} ]

        """
        self.T                      =   System_Lib().T
        locals().update(                self.T.__getdict__())
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

    def __init__(self):

        self.T                      =   System_Lib().T
        T                           =   self.T
        locals().update(                T)
        s                           =   System_Servers()
        self.servers                =   s.servers
        self.worker                 =   s.worker
        self.reporter               =   System_Reporter()
        c                           =   pd.read_sql('select * from crons',sys_eng)
        self.crons                  =   c

    def check_log_rotate(self):

        self.process                =   'check_logrotate'
        self.process_start          =   dt.now()
        self.process_params         =   {}
        self.process_stout          =   []
        self.process_sterr          =   None

        (_out,_err)                 =   exec_cmds(['cat /etc/logrotate.d/sv_syslog'],self.worker,self.worker)
        assert _err==None
        if _out.find('weekly')!=-1:
            rotate_period           =   7

        cmds                        =   ['cat /var/lib/logrotate/status | grep syslogs | grep -v \'tmp_\'']
        (_out,_err)                 =   exec_cmds(cmds,self.worker,self.worker)
        assert _err==None
        today                       =   dt.now()
        report_failure              =   False
        for it in _out.split('\n'):
            if it!='':
                t                   =   it.split()[1]
                z                   =   t[:t.rfind('-')]
                cron_d              =   dt.strptime(z,'%Y-%m-%d')
                y                   =   cron_d-today
                days_since          =   abs(y.days)
                if days_since>rotate_period:
                    report_failure  =   True

        self.process_end            =   dt.now()
        if report_failure:
            self.process_stout.append(  'LogRotate does not appear to be working on %s' % self.worker )
            results_and_errors      =   ['results_log','errors_paste_log_txt']
        else:
            self.process_stout.append(  'LogRotate looks good on %s' % self.worker )
            results_and_errors      =   ['results_log']

        return self.reporter.manage(self,results_and_errors=results_and_errors)

    def find_new_pip_libs(self,vars):
        """

        usage:
            python System_Control.py cron find_new_pip_libs
            python System_Control.py cron find_new_pip_libs ub1
            python System_Control.py cron find_new_pip_libs ub1 ub2

        """

        if len(vars)==0:
            SERVS                   =   self.servers[self.servers.pip_libs.isnull()==False].server.tolist()
        else:
            SERVS                   =   vars

        self.process                =   'find_new_pip_libs'
        self.process_start          =   dt.now()
        self.process_params         =   {'SERVS'             :   SERVS }
        self.process_stout          =   []
        self.process_sterr          =   []

        for serv in SERVS:
            cmds                    =   ['echo $HOME;',
                                         'a=$(which grep);',
                                         'locate /ENV | $a -E \'/ENV$\'']
            (_out,_err)             =   exec_cmds(cmds,serv,self.worker)
            self.process_sterr.append(  _err)
            serv_home               =   _out.split('\n')[0]
            found_lib_locs          =   [ it for it in _out.split('\n')[1:] if it.count(serv_home)>0 ]
            saved_libs              =   self.servers[self.servers.tag==serv].pip_libs.tolist()[0]
            known_lib_locs          =   [ saved_libs[it]['location'] for it in saved_libs.keys() ]
            new_lib_locs            =   [ it for it in found_lib_locs if known_lib_locs.count(it)==0 ]
            if not hasattr(self,'ignore_lib_D'):
                self.health         =   System_Health()
                self.ignore_lib_D   =   dict(zip(self.health.ignore.param2.tolist(),
                                                self.health.ignore.server_tag.tolist()))

            to_save_locs            =   [ it for it in new_lib_locs if (self.ignore_lib_D.has_key(it)==False and it!='') ]

            if to_save_locs:

                # update dict from DB
                lib_names           =   []
                for it in to_save_locs:
                    lib_name        =   it[it.rstrip('/ENV').rfind('/')+1:].rstrip('/ENV')
                    pt              =   1
                    while saved_libs.keys().count(lib_name)>0:
                        if saved_libs.keys().count(lib_name+'_'+str(pt))==0:
                            lib_name=   lib_name+'_'+str(pt)
                        else:   pt +=   1
                    lib_names.append(   lib_name)
                    lib_info        =   {lib_name               :   { 'requirements':'','location':it }   }
                    saved_libs.update(  lib_info)
                    self.process_stout.append(['new_pip_lib',serv,lib_name,it])

                # update DB with updated dict
                conn.set_isolation_level(0)
                f_saved_libs        =   str(saved_libs).replace("u'",'"').replace("'",'"')
                cmd                 =   """ update servers set pip_libs='%s' where tag='%s' """ % (f_saved_libs,serv)
                cur.execute(            cmd)

                # Run backup_pip to save lib reqs to paste
                if not hasattr(self,'SYS'):
                    self.SYS        =   System_Admin()
                vars                =   [serv] + lib_names
                self.SYS.backup_pip( *vars )


        self.process_end            =   dt.now()
        return self.reporter.manage(    self,results_and_errors=['results_paste_log_txt'])

    def run_git_fsck(self):
        self.process                =   'git_fsck'
        self.process_start          =   dt.now()
        self.process_params         =   {}
        self.process_stout          =   []
        self.process_sterr          =   None
        g                           =   pd.read_sql('select * from servers where git_tag is not null',sys_eng)
        sub_srcs,sub_dest           =   g.git_sub_src.tolist(),g.git_sub_dest.tolist()
        master_src                  =   g.git_master_src.tolist()
        all_repos                   =   sub_srcs + sub_dest + master_src
        all_repos                   =   sorted(dict(zip(all_repos,range(len(all_repos)))).keys())
        serv                        =   '0'
        for it in all_repos:
            if it.find(serv)!=0:
                serv                =   it[it.find('@')+1:it.rfind(':')]
            s_path                  =   it[it.rfind(':')+1:]
            cmds                    =   ['cd %s;' % s_path,
                                         'git fsck;']
            (_out,_err)             =   exec_cmds(cmds,serv,self.worker)
            assert _err==None
            if _out!='':
                msg                 =   'Repo needs work >>%s<<' % it
                self.process_stout.append( msg )

        self.process_end            =   dt.now()
        if not self.process_stout:
            self.process_stout.append(  'Repos look good' )
            results_and_errors      =   ['results_log']
        else:
            results_and_errors      =   ['results_paste_log_txt']

        return self.reporter.manage(    self,results_and_errors=results_and_errors)

    def authorize(self,vars):
        self.process_start          =   dt.now()

        if len(vars)==0:
            assert 'No cmd requested for auth'==False
        elif len(vars)==1:
            cron_tag,cron_cmd       =   vars[0:2]
            results_and_errors      =   ['results_log','errors_paste_log_txt']
        else:
            cron_tag,cron_cmd       =   vars[0:2]
            results_and_errors      =   vars[2:]

        self.process                =   cron_tag
        self.process_params         =   {'cmd' : cron_cmd}
        # cmds                        =   ['echo "%s" | sudo -S -k --prompt=\'\' ' % PASS,
        #                                  'bash -i -l -c "%s";' % cron_cmd]
        cmds                        =   [''.join(["SCR_OPT=$(if [ -n $(env | grep -E '^HOME' | grep 'Users/admin') ];",
                                                  ' then echo "-qc"; else echo "-q"; fi;);']),
                                         'echo "%s" | sudo -S --prompt=\'\' ' % PASS,
                                         'script $SCR_OPT \"bash -i -l -c \'',
                                         '%s' % cron_cmd,
                                         '\'\";',
                                         'echo "%s" | sudo -S --prompt=\'\' rm -f typescript;' % PASS,
                                         'unset SCR_OPT;',
                                        ]
        (_out,_err)                 =   exec_cmds(cmds,self.worker,self.worker)

        self.process_stout          =   _out
        self.process_sterr          =   _err
        self.process_end            =   dt.now()
        return self.reporter.manage(    self,results_and_errors=results_and_errors)

class System_Health:

    def __init__(self):
        self.T                      =   System_Lib().T
        locals().update(                self.T.__getdict__())
        s                           =   System_Servers()
        self.servers                =   s.servers
        self.worker                 =   s.worker
        h                           =   pd.read_sql('select * from system_health',sys_eng)
        self.reporter               =   System_Reporter()
        self.processes              =   h[h.type_tag=='process'].copy()
        self.mounts                 =   h[h.type_tag=='mount'].copy()
        self.checks                 =   h[h.type_tag=='check'].copy()
        self.ignore                 =   h[h.type_tag=='ignore'].copy()

    def make_display_check(self,chk_sys):
        self.process                =   'System_Health_Check'
        self.process_start          =   dt.now()
        self.process_params         =   {}
        self.process_stout          =   []
        self.process_sterr          =   []
        P                           =   self.processes
        procs                       =   P[ P.server_tag==chk_sys ].ix[:,['param1','param2']]
        procs                       =   dict(zip(procs.param1.tolist(),procs.param2.tolist()))

        if  chk_sys                !=   self.worker:
            t                       =   'ssh %s "ps -axww"'%chk_sys
            cmd                     =   shlex.split(t)
        else: cmd                   =   ['ps','-axww']

        p                           =   sub_popen(cmd,stdout=sub_PIPE)
        (ap, err)                   =   p.communicate()
        res,errs                    =   [],[]
        for k in sorted(procs.keys()):

            if len(re_findall(procs[k],ap))==0:
                res.append(             "[$(tput setaf 1 && tput bold)chk$(tput setaf 9 && `tput rmso`)]$'\t'%s"%k)
                errs.append(            'Issue on "%s" with process: "%s"' % (chk_sys,k) )
            else:
                res.append(             "[$(tput bold && tput setaf 2)ok$(tput setaf 9 && `tput rmso`)]$'\t'%s"%k)

        C                           =   self.checks
        checks                      =   C[ C.server_tag==chk_sys ].ix[:,['param1','param2']]
        checks                      =   dict(zip(checks.param1.tolist(),checks.param2.tolist()))

        for k in sorted(checks.keys()):

            cmd                     =   checks[k]
            if chk_sys!=self.worker:
                cmd                 =   "ssh %s '%s'" % (chk_sys,cmd)
            p                       =   sub_popen(cmd,stdout=sub_PIPE,shell=True)
            (_out,_err)             =   p.communicate()
            if _out.find('0')==-1:
                res.append(             "[$(tput bold && tput setaf 2)ok$(tput setaf 9 && `tput rmso`)]$'\t'%s"%k)
            else:
                res.append(             "[$(tput setaf 1 && tput bold)chk$(tput setaf 9 && `tput rmso`)]$'\t'%s"%k)
                errs.append(            'Issue on "%s" with check: "%s"' % (chk_sys,k))


        print '<>'.join(                res)

        self.process_sterr          =   errs if errs else None
        self.process_end            =   dt.now()
        if SYS_HEALTH_TXT_ERRORS:
            return self.reporter.manage(self,results_and_errors='errors_paste_log_txt')

class System_Databases:

    def __init__(self):
        self.T                      =   System_Lib().T
        self.databases              =   self.T.pd.read_sql('select * from databases where is_active is True',sys_eng)

class System_Servers:

    def __init__(self,_parent=None):
        self.T                      =   System_Lib().T
        locals().update(                self.T.__getdict__())
        shares                      =   pd.read_sql('select * from shares',sys_eng)
        self.sh                     =   shares
        s                           =   pd.read_sql('select * from servers where production_usage is not null',sys_eng)
        self.s                      =   s
        server_dir_dict             =   dict(zip(s.tag.tolist(),s.home_dir.tolist()))
        mac                         =   [int(str(get_mac()))]
        worker                      =   s[ s.mac.isin(mac) & s.home_dir.isin([os_environ['HOME']]) ].iloc[0].to_dict()
        self.worker                 =   worker['server']
        self.worker_host            =   worker['host']
        global THIS_SERVER
        THIS_SERVER                 =   self.worker
        self.base_dir               =   worker['home_dir']
        self.server_idx             =   worker['server_idx']
        rank                        =   {'high':3,'medium':2,'low':1,'none':0}
        s['ranking']                =   s.production_usage.map(rank)
        self.priority               =   dict(zip(s.tag.tolist(),s.ranking.tolist()))
        self.mgr                    =   self

    def mnt_sshfs(self,mnt_src,mnt_as_vol):

        sshfs                       =   self.T.os_environ['SSHFS']+' '
        cmds                        =   ['umount %s > /dev/null 2>&1; ' % mnt_as_vol,
                                         'mkdir -p %s ;' % mnt_as_vol,
                                         '%s %s %s -o ConnectTimeout=5 2>&1 ; ' % (sshfs,mnt_src,mnt_as_vol),]

        try:
            (_out,_err)             =   self.T.exec_cmds(cmds)
            if _out.count('Connection reset'):
                print                   mnt_src,'mount failed'

        except:

            print                       mnt_src,'mount failed'
            (_out,_err)             =   self.T.exec_cmds(['rm -fR %s ; ' % mnt_as_vol])
            assert _err            is   None


        return

    def mnt_shares(self,shares=[]):
        

        if not shares:
            shares                  =   map(lambda s: str(s.strip("'")), 
                                            self.s[self.s.tag==self.worker].mnt_up.tolist()[:][0] )
            shares_D                =   dict(zip([ '/Volumes/' + it for it in shares ],
                                                 [ '%s:/' % it for it in shares ]))

        elif shares[:].count('dev'):
            shares                  =   map(lambda s: str(s.strip("'")), 
                                            self.s[self.s.tag==self.worker].mnt_dev.tolist()[:][0] )
            shares_D                =   dict(zip([ '/Volumes/' + it for it in shares ],
                                                 [ '%s:/' % it for it in shares ]))

        elif shares[:].count('all'):
            new_shares              =   self.sh[self.sh.remote_path.str.contains(self.worker)==False]
            shares_D                =   dict(zip(new_shares.tag.tolist(),new_shares.remote_path.tolist()))
        
        else:
            mnt_srcs                =   map(lambda it: '%s:/' % it if not self.sh[self.sh.tag==it].remote_path.tolist() 
                                                        else self.sh[self.sh.tag==it].remote_path.tolist()[0],shares)
            shares_D                =   dict(zip([ '/Volumes/' + it for it in shares ],
                                                 mnt_srcs))

        (_out,_err)                 =   self.T.exec_cmds(['ps','-axww'])
        assert _err                is   None

        for mnt_as_vol,mnt_src in shares_D.iteritems():
            if not re_findall(mnt_as_vol,_out):
                self.mnt_sshfs(         mnt_src,mnt_as_vol)

        return

    # def umnt_shares(self,dirs=['all'],local=True):

    #     if dirs  == ['all']:            dirs = self.T.keys()
    #     elif dirs==['mnt_s1_always']:   dirs = ['ub2','mbp2']
    #     elif dirs==['mnt_s2_always']:   dirs = ['mbp2','ub1']
    #     elif dirs==['mnt_s3_always']:   dirs = ['ub2','ub1']

    #     dirs                        =   [it for it in dirs if it!=self.worker]
    #     for it in dirs:

    #         cmd                     =   'ps -A | grep ssh | grep -v grep | awk '+"'{print $5}'"
    #         p                       =   sub_popen([cmd], stdout=sub_PIPE, shell=True)
    #         (t, err)                =   p.communicate()
    #         chk                     =   t.split('\n')

    #         if chk.count(self.T[it])!=0:
    #             cmd                 =   ['umount /Volumes/%s && rmdir /Volumes/%s'%(it,it)]
    #             proc                =   sub_popen(cmd, stdout=sub_PIPE, shell=True)
    #             (t, err)            =   proc.communicate()
    #             delay(3)

    #     return True

class System_Admin:

    def __init__(self):
        self.T                      =   System_Lib().T
        locals().update(                self.T.__getdict__())
        s                           =   System_Servers()
        self.servers                =   s.servers
        self.worker                 =   s.worker
        self.base_dir               =   s.base_dir
        self.priority               =   s.priority
        self.ready                  =   s.mnt_shares(['ub2','ub1','ub3'])
        # self.cfg                   =   self.get_cfg()
        self.params                 =   {}
        # self.dry_run               =   True
        self.dry_run                =   False
        self.reporter               =   System_Reporter()
        self.pb                     =   self.reporter.pb

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

    def add_options(self):
        options                     =   [ 'verbose','verbose','recursive','archive','update',
                                          'one-file-system','compress','prune-empty-dirs',
                                          'itemize-changes']
                                        #,"filter='dir-merge /.rsync-filter'"]
			                            # ,'delete-before'
        if self.dry_run==True:          options.append('dry-run')
        self.params.update(             { 'options'     :   map(lambda s: '--%s'%s,options) })

    def add_exclusions(self):
        exclude                     =   self.cfg.exclude.map(lambda s: '--exclude='+str(s)).tolist()
        if len(exclude)!=0:
            self.params.update(         { 'exclusions':   exclude, })

    def add_inclusions(self):
        include                     =   self.cfg.include.map(lambda s: '--include='+str(s)).tolist()
        if len(include)!=0:
            self.params.update(         { 'inclusions':   include, })

    def add_logging(self):
        self.params.update(             { 'logging'     :   ['--outbuf=L'], })

    def backup_ipython(self,params=''):
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

    def backup_databases(self,params=''):
        self.process                =   'backup_databases'
        self.process_start          =   dt.now()
        self.process_params         =   {}
        self.process_stout          =   []
        d                           =   System_Databases()
        self.databases              =   d.databases
        self.database_names         =   self.databases.db_name.tolist()
        for i in range(len(self.databases)):
            T                       =   {'started'                  :   dt.isoformat(dt.now())}
            db_info                 =   self.databases.ix[i,['backup_path','db_server','db_name','backup_cmd']].map(str)
            serv_info               =   self.servers[self.servers.git_tag==db_info['db_server']].iloc[0,:].to_dict()

            T.update(                   {'DB'                       :   '%s @ %s' % (db_info['db_name'],
                                                                                     serv_info['server'])})

            fpath                   =   '%s/%s_%s_%s.sql' % tuple(db_info[:-1].tolist() + [dt.strftime(dt.now(),'%Y_%m_%d')])
            fname                   =   fpath[fpath.rfind('/')+1:]
            cmd                     =   """%s -d %s -h 0.0.0.0 -p 8800 --username=postgres > %s
                                        """.replace('\n','').replace('\t','').strip() % (db_info['backup_cmd'],
                                                                                         db_info['db_name'],
                                                                                         fpath)
            (_out,_err)             =   exec_cmds([cmd],serv_info['server'],self.worker)
            assert _out==''
            assert _err==None

            cmds                    =   ['scp %(host)s@%(serv)s:%(fpath)s /Volumes/EXT_HD/.pg_dump/;'
                                         % ({ 'host'                :   serv_info['host'],
                                              'serv'                :   serv_info['server'],
                                              'fpath'               :   fpath })]

            (_out,_err)                 =   exec_cmds(cmds,'ub1',self.worker)
            assert _out==''
            assert _err==None

            T.update(                       {   'ended'             :   dt.isoformat(dt.now())} )

            self.process_stout.append(      T )

        self.process_sterr              =   None
        self.process_end                =   dt.now()
        return self.reporter.manage(        self,results_and_errors=['results_paste_log'])

    def backup_system(self,params=''):
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

    def backup_pip(self,*vars):
        """
        usage:
            python System_Control.py backup_pip
            python System_Control.py backup_pip ub2
            python System_Control.py backup_pip ub2 ipython
            python System_Control.py backup_pip ub2 ipython aprinto
        """


        if   len(vars)==0:
            SERVS                       =   self.servers[self.servers.pip_libs.isnull()==False].server.tolist()
            spec_libs                   =   []
        elif len(vars)==1:
            SERVS,spec_libs             =   [vars[0]],[]
        elif len(vars)>1:
            SERVS,spec_libs             =   [vars[0]],vars[1:]
        else:
            assert 'Specified server on which to backup_pip'==False


        self.process                    =   'backup_pip'
        self.process_start              =   dt.now()
        self.process_params             =   {'SERVS'             :   SERVS }
        self.process_stout              =   []
        for serv in SERVS:

            libs,save_libs              =   {},{}
            if len(spec_libs)==0:
                libs                    =   self.servers[ self.servers.tag==serv ].pip_libs.tolist()[0]
            else:
                all_libs                =   self.servers[ self.servers.tag==serv ].pip_libs.tolist()[0]
                for it in all_libs.keys():
                    if spec_libs.count(it)>0:
                        libs.update({       it                  :   all_libs[it] }  )
                    else:
                        save_libs.update({  it                  :   all_libs[it] }  )

            self.process_stout.append(      { '%s_pip_libs'%serv  :   str(libs) })


            D,old_reqs                  =   {},[]
            for k,v in libs.iteritems():

                if v['requirements']!='':
                    old_reqs.append(        v['requirements'].replace('http://pastebin.com/','')  )

                lib_loc                 =   v['location']
                cmds                    =   ['cd %s' % lib_loc]
                if lib_loc.find('ENV')>0:
                    cmds.append(            'source bin/activate'  )
                cmds.append(                'pip freeze'  )

                cmd                     =   '; '.join(cmds)
                if serv!=self.worker:
                    cmd                 =   "ssh %s '%s'" % (serv,cmd)

                proc                    =   sub_check_output(cmd, stderr=sub_stdout, shell=True)

                pb_url                  =   self.pb.createPaste(  proc,
                                            api_paste_name='%s -- pip_lib: %s' % (serv,k),
                                            api_paste_format='',
                                            api_paste_private='1',
                                            api_paste_expire_date='N')

                D.update(                   { k     :   {'location'     :   lib_loc,
                                                         'requirements' :   pb_url }
                                            })

                # Append any libs not updated
                for k,v in save_libs.iteritems():
                    D.update(               { k     :   v }  )

                # Push to servers DB
                cmd                     =   """
                                                UPDATE servers SET
                                                pip_libs            =   '%s',
                                                pip_last_updated    =   'now'::timestamp with time zone
                                                WHERE tag = '%s'
                                            """ % (j_dump(D),serv)

                conn.set_isolation_level(   0)
                cur.execute(                cmd   )

                # Delete old Pastes
                for it in old_reqs:
                    self.pb.deletePaste(    it)



        self.process_sterr              =   [None]
        self.process_end                =   dt.now()

        return self.reporter.manage(        self,results_and_errors=['results_paste_log'])

    def install_pip(self,*vars):
        """
        usage: python System_Control.py install pip_lib [dest_serv] [dest_serv_path] [source_serv_lib] [source_lib] [option]

        e.g.,
            python System_Control.py install pip_lib ub2 $HOME/.scripts/ENV ub3 aprinto
            python System_Control.py install pip_lib ub1 $HOME/.scripts/ENV ub2 .scripts
            python System_Control.py install pip_lib ub2 $HOME/.scripts/ENV mbp2 ipython upgrade
            python System_Control.py install pip_lib ub2 $HOME/.scripts/ENV mbp2 ipython upgrade overwrite
        """
        self.process                    =   'install_pip'
        self.process_start              =   dt.now()

        assert len(vars) >= 4

        to_serv,to_path                 =   vars[0:2]

        serv                            =   self.servers[self.servers.tag==to_serv].iloc[0,:].to_dict()
        to_path                         =   to_path % serv

        to_dir,env_dir                  =   to_path[:to_path.rfind('/')],to_path[to_path.rfind('/')+1:]
        from_serv,from_lib              =   vars[2:4]
        options                         =   ['']

        results_and_errors              =   []
        if len(vars)>=5:
            for it in vars[4:]:
                if it.find('errors_')==0 or it.find('result_')==0:
                    with_errors.append(     it)
                else:
                    options.append(         it)
        if len(results_and_errors)==0:
            results_and_errors          =   ['results_log','errors_paste_log']

        self.process_params             =   {'to_serv'          :   to_serv,
                                             'to_path'          :   to_path,
                                             'from_serv'        :   from_serv,
                                             'from_lib'         :   from_lib,
                                             'options'          :   options,}

        z                               =   pd.read_sql("select pip_libs from servers where tag = '%s'"%from_serv,sys_eng)
        t                               =   z.pip_libs.tolist()[0][from_lib]['requirements']

        reqs                            =   self.pb.getPasteRawOutput(t[t.rfind('/')+1:]).split('\n')
        if options.count('upgrade')==1:
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
        if options.count('overwrite')==0:
            cmds.append(                    'if [ -d "%s" ]; then echo "DEST PATH ALREADY EXISTS" && exit 1; fi;' % to_path)


        (_out,_err)                     =   exec_cmds(cmds,to_serv,self.worker)
        assert _err==None
        assert _out.find('No such file or directory')==-1
        assert _out.find('command not found')==-1
        assert _out.find('DEST PATH NOT EXIST')==-1
        assert _out.find('DEST PATH ALREADY EXISTS')==-1


        script                          =   ['#!/bin/bash',
                                             'echo "install_env started"',
                                             'cd %s' % to_dir]

        if options.count('overwrite')==1:
            script.append(                  'rm -fR %s/' % env_dir)

        script.extend(                      ['pip install --upgrade pip || exit 1',
                                             'virtualenv ENV || exit 1',
                                             'source ENV/bin/activate  || exit 1',
                                             'pip install --upgrade pip'] )

        line_cmd                        =   ' '.join(['pip install --allow-all-external --allow-unverified %(lib)s',
                                                      '%(lib_v)s',
                                                      '|| echo "Error installing %(lib)s"'])

        script.extend(                      [ line_cmd % {'lib':it[:it.find(version_spec)],'lib_v':it} for it in reqs ])
        script.extend(                      ['echo "install_env complete"'])
        with open('/tmp/install_env','w') as f:
            f.write(                        '\n'.join(script))

        os_cmd(                             'chmod +x /tmp/install_env')

        if to_serv!=self.worker:
            cmds                        =   ['scp %s@%s:/tmp/install_env /tmp/ 2>&1;' % (self.worker,self.worker),
                                             '/tmp/install_env 2>&1;',
                                             'rm /tmp/install_env;']
            (_out,_err)                 =   exec_cmds(cmds,to_serv,self.worker)
        else:
            (_out,_err)                 =   exec_cmds(['/tmp/install_env 2>&1','rm /tmp/install_env'],self.worker,self.worker)
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

        return self.reporter.manage(self,results_and_errors=results_and_errors)

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

    def to_pastebin(self,params=''):
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

    def run_rsync(self):
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

class System_Lib:

    def __init__(self):
        import                                  sys
        import                                  codecs
        # reload(sys)
        # sys.setdefaultencoding('UTF8')
        from py_classes                     import To_Class
        from uuid                           import getnode          as get_mac
        from os                             import system           as os_cmd
        from os                             import environ          as os_environ
        from os                             import access           as os_access
        from os                             import X_OK             as os_X_OK
        from os                             import mkdir            as os_mkdir
        from traceback                      import format_exc       as tb_format_exc
        from types                          import NoneType
        from subprocess                     import Popen            as sub_popen
        from subprocess                     import check_output     as sub_check_output
        from subprocess                     import PIPE             as sub_PIPE
        from subprocess                     import STDOUT           as sub_stdout
        import                                  shlex
        from time                           import sleep            as delay
        from uuid                           import uuid4            as get_guid
        from datetime                       import datetime         as dt
        from json                           import dumps            as j_dump
        from re                             import findall          as re_findall
        from sqlalchemy                     import create_engine
        import                                  pandas           as pd
        from system_settings                import DB_HOST,DB_PORT,DB_NAME,THIS_IP,PASS,THIS_PC,BASE_DIR
        from system_settings                import SYS_HEALTH_TXT_ERRORS,ELASTIC_SEARCH_CPU_LIMIT
        from system_settings                import SYSLOG_CPU_LIMIT,KIBANA_CPU_LIMIT
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

        D                                   =   {'exec_cmds'    :   self.exec_cmds,
                                                 'guid'         :   str(get_guid().hex)[:7]}
        D.update(                               {'tmp_tbl'      :   'tmp_'+D['guid']})
        self.T                              =   To_Class(D)
        all_imports                         =   locals().keys()
        excludes                            =   ['D','To_Class']
        for k in all_imports:
            if not excludes.count(k):
                self.T.update(                  {k              :   eval(k) })
        globals().update(                       self.T.__getdict__())

    def exec_cmds(self,cmds,cmd_host='',this_worker=''):
        cmd                             =   ' '.join(cmds)
        if cmd_host==this_worker:
            p                           =   sub_popen(cmd,stdout=sub_PIPE,shell=True)
        else:
            cmd                         =   "ssh %s '%s'" % (cmd_host,cmd)
            p                           =   sub_popen(cmd,stdout=sub_PIPE,shell=True)
        return p.communicate()



from sys import argv
if __name__ == '__main__':
    return_var                          =   None
    if len(argv)>1:

        if argv[1].find('backup_')==0:
            SYS                         =   System_Admin()
            if (len(argv)>2 and argv[2]=='dry-run'):
                SYS.dry_run             =   True
            elif len(argv)>2:
                vars                    =   argv[2:]
            else:
                vars                    =   []


            if  argv[1]=='backup_all':
                SYS.backup_ipython(         )
                SYS.backup_databases(       )
                SYS.backup_system(          )
                SYS.backup_pip(             )


            elif  argv[1]=='backup_ipython':     SYS.backup_ipython()
            elif  argv[1]=='backup_databases':   SYS.backup_databases()
            elif  argv[1]=='backup_system':      SYS.backup_system()
            elif  argv[1]=='backup_pip':         SYS.backup_pip(*vars)


        elif argv[1]=='install':
            SYS                         =   System_Admin()
            if   argv[2]=='pip_lib':
                SYS.install_pip(            *argv[3:])

        elif argv[1]=='check_health':
            SYS                         =   System_Health()
            if len(argv)==3:
                SYS.make_display_check(     argv[2])
            else:
                for it in ['mbp2','ub1','ub2','ub3']:
                    SYS.make_display_check( it )

        elif argv[1]=='cron':
            CRON                        =   System_Crons()
            if   argv[2]=='logrotate':
                CRON.check_log_rotate(      )
            elif argv[2]=='git_fsck':
                CRON.run_git_fsck(          )
            elif argv[2]=='find_new_pip_libs':
                CRON.find_new_pip_libs(     argv[3:])
            elif argv[2]=='authorize':
                CRON.authorize(             argv[3:])

        elif argv[1]=='settings':
            CFG                         =   System_Config()
            return_var                  =   CFG.adjust_settings( *argv[2:] )

        elif ['mnt','umnt'].count(argv[1]):
            SERVS                       =   System_Servers()
            return_var                  =   SERVS.mnt_shares(argv[2:]) if argv[1]=='mnt' else SERVS.umnt_shares(argv[2:])




        if return_var:                      print return_var
