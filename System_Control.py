# Libraries
import                                 sys
import                                 codecs
# reload(sys)
# sys.setdefaultencoding('UTF8')
from uuid                       import getnode          as get_mac
from os                         import system           as os_cmd
from os                         import environ          as os_environ
from os                         import mkdir            as os_mkdir
from subprocess                 import Popen            as sub_popen
from subprocess                 import check_output     as sub_check_output
from subprocess                 import PIPE             as sub_PIPE
from subprocess                 import STDOUT           as sub_stdout
import shlex
from time                       import sleep            as delay
from datetime                   import datetime         as dt
from json                       import dumps            as j_dump
from re                         import findall          as re_findall
from sqlalchemy                 import create_engine
import                                 pandas           as pd
import                                 psycopg2

pd.set_option('expand_frame_repr',False)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 1000)
pd.set_option('display.width',180)
np = pd.np
np.set_printoptions(linewidth=200,threshold=np.nan)

sys_eng = create_engine(r'postgresql://postgres:postgres@192.168.3.52:8800/system',
                       encoding='utf-8',
                       echo=False)

conn = psycopg2.connect("dbname='system' user='postgres' host='192.168.3.52' password='' port=8800");
cur = conn.cursor()

global THIS_SERVER
#from IPython import embed_kernel as embed; embed()
# from ipdb import set_trace as i_trace; i_trace()

def exec_cmds(cmds,cmd_host,this_worker):
    cmd                         =   ' '.join(cmds)
    if cmd_host==this_worker:
        p                       =   sub_popen(cmd,stdout=sub_PIPE,shell=True)
    else:
        cmd                     =   "ssh %s '%s'" % (cmd_host,cmd)
        p                       =   sub_popen(cmd,stdout=sub_PIPE,shell=True)
    return p.communicate()



class PasteBin:
    """
    Module:             http://pythonhosted.org/pastebin_python/code.html

    Expiration Format:  (see http://pastebin.com/api#6)
        Input     Description
        'N'       Never
        '10M'     10 minutes
        '1H'      1 hour
        '1D'      1 day
        '1W'      1 week
        '2W'      2 weeks
        '1M'      1 month

    Publication Format:  public = 0, unlisted = 1, private = 2
    """
    def __init__(self):
        from pastebin_python import PastebinPython
        user_name       =   'mech_coder'
        passw           =   'Delivery100%'
        dev_key         =   '4f26d1cb7a08f03b02ab24dae43bc431'
        pb              =   PastebinPython(api_dev_key=dev_key)
        pb.createAPIUserKey(user_name,passw)
        self.pb         =   pb

class System_Crons:

    def __init__(self):
        s                           =   System_Servers()
        self.servers                =   s.servers
        self.worker                 =   s.worker
        c                           =   pd.read_sql('select * from crons',sys_eng)
        self.crons                  =   c

    def check_log_rotate(self):

        (_out,_err)                 =   exec_cmds(['cat /etc/logrotate.d/sv_syslog'],self.worker,self.worker)
        if _out.find('weekly')!=-1:
            rotate_period           =   7

        cmds                        =   ['cat /var/lib/logrotate/status | grep syslogs | grep -v \'tmp_\'']
        (_out,_err)                 =   exec_cmds(cmds,self.worker,self.worker)
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

        if report_failure:
            msg                     =   'LogRotate does not appear to be working'

            cmd                     =   'logger -t "CRON" "%s"' % msg
            proc                    =   sub_popen([''.join(cmd)], stdout=sub_PIPE, shell=True)
            (t, err)                =   proc.communicate()

            cmd                     =   'echo "%s" | mail -t 6174295700@vtext.com' % msg
            proc                    =   sub_popen([''.join(cmd)], stdout=sub_PIPE, shell=True)
            (t, err)                =   proc.communicate()

        else:
            msg                     =   'LogRotate looks good'

            cmd                     =   'logger -t "CRON" "%s"' % msg
            proc                    =   sub_popen([''.join(cmd)], stdout=sub_PIPE, shell=True)
            (t, err)                =   proc.communicate()

    def run_git_fsck(self):
        g                           =   pd.read_sql('select * from servers where git_tag is not null',sys_eng)
        # check all sub_source
        #       add new master_sources
        # check master sources
        sub_srcs,sub_dest           =   g.git_sub_src.tolist(),g.git_sub_dest.tolist()
        master_src                  =   g.git_master_src.tolist()
        all_repos                   =   sub_srcs + sub_dest + master_src
        all_repos                   =   sorted(dict(zip(all_repos,range(len(all_repos)))).keys())
        serv,troubled_repos         =   '0',[]
        for it in all_repos:
            if it.find(serv)!=0:
                serv                =   it[it.find('@')+1:it.rfind(':')]
            s_path                  =   it[it.rfind(':')+1:]
            cmds                    =   ['cd %s;' % s_path,
                                         'git fsck;']
            (_out,_err)             =   exec_cmds(cmds,serv,self.worker)
            assert _err==None
            if _out!='':
                troubled_repos.append(  it )

                msg                 =   'Repo needs work >>%s<<' % it

                cmd                 =   'logger -t "CRON" "%s"' % msg
                proc                =   sub_popen([''.join(cmd)], stdout=sub_PIPE, shell=True)
                (t, err)            =   proc.communicate()

                cmd                 =   'echo "%s" | mail -t 6174295700@vtext.com' % msg
                proc                =   sub_popen([''.join(cmd)], stdout=sub_PIPE, shell=True)
                (t, err)            =   proc.communicate()

        if troubled_repos==[]:
            msg                     =   'Repos look good'

            cmd                     =   'logger -t "CRON" "%s"' % msg
            proc                    =   sub_popen([''.join(cmd)], stdout=sub_PIPE, shell=True)
            (t, err)                =   proc.communicate()

        # from ipdb import set_trace as i_trace; i_trace()

class System_Health:

    def __init__(self):
        s                   =   System_Servers()
        self.servers        =   s.servers
        self.worker         =   s.worker
        h                   =   pd.read_sql('select * from system_health',sys_eng)
        self.checks         =   h

    def make_display_check(self,chk_sys):
        H                   =   self.checks
        procs               =   H[ (H.type_tag=='process') & (H.server_tag==chk_sys) ].ix[:,['param1','param2']]
        procs               =   dict(zip(procs.param1.tolist(),procs.param2.tolist()))

        if  chk_sys        !=   self.worker:
            t               =   'ssh %s "ps -axww"'%chk_sys
            cmd             =   shlex.split(t)
        else: cmd           =   ['ps','-axww']

        p                   =   sub_popen(cmd,stdout=sub_PIPE)
        (ap, err)           =   p.communicate()
        res                 =   []
        for k in sorted(procs.keys()):

            if len(re_findall(procs[k],ap))==0:
                res.append("[$(tput setaf 1 && tput bold)chk$(tput setaf 9 && `tput rmso`)]$'\t'%s"%k)
            else:
                res.append("[$(tput bold && tput setaf 2)ok$(tput setaf 9 && `tput rmso`)]$'\t'%s"%k)

        checks              =   H[ (H.type_tag=='check') & (H.server_tag==chk_sys) ].ix[:,['param1','param2']]
        checks              =   dict(zip(checks.param1.tolist(),checks.param2.tolist()))

        for k in sorted(checks.keys()):

            cmd             =   checks[k]
            if chk_sys!=self.worker:
                cmd         =   "ssh %s '%s'" % (chk_sys,cmd)
            # cmd             =   shlex.split(cmd)
            p               =   sub_popen(cmd,stdout=sub_PIPE,shell=True)
            (_out,_err)     =   p.communicate()
            if _out.find('0')==-1:
                res.append("[$(tput bold && tput setaf 2)ok$(tput setaf 9 && `tput rmso`)]$'\t'%s"%k)
            else:
                res.append("[$(tput setaf 1 && tput bold)chk$(tput setaf 9 && `tput rmso`)]$'\t'%s"%k)

        print '<>'.join(res)

class System_Databases:

    def __init__(self):
        self.databases  =   pd.read_sql('select * from databases where active is True',sys_eng)

class System_Servers:

    def __init__(self):
        L   =   {
         'BD_Scripts'   :   'ub2:/home/ub2/BD_Scripts',
         'gDrive'       :   'ub2:/home/ub2/gDrive',
         'GIS'          :   'ub2:/home/ub2/GIS',
         '.ipython'     :   'ub2:/home/ub2/.ipython',
         'Reference'    :   'ub2:/home/ub2/Reference',
         'SERVER1'      :   'ub1:/home/ub1/SERVER1',
         'SERVER2'      :   'ub2:/home/ub2/SERVER2',
         'SERVER3'      :   'mbp2:/Users/admin/SERVER3',
         'SERVER4'      :   'ub3:/home/ub3/SERVER4',
         'SERVER5'      :   'serv:/home/jail/home/serv/system_config/SERVER5',
         'ub1'          :   'ub1:/',
         'ub2'          :   'ub2:/',
         'ub3'          :   'ub3:/',
         'mbp2'         :   'mbp2:/',
         'ms1'          :   'ms1:/',
         'serv'         :   'serv:/home/jail'}

        R   =   {}
        for k,v in R.iteritems():
            if v[0]=='m':   R.update({k:v.replace(':','_remote:')})
            else:           R.update({k:v})
        self.L          =   L
        self.R          =   R
        s               =   pd.read_sql('select * from servers where production_usage is not null',sys_eng)
        self.servers    =   s
        server_dir_dict =   dict(zip(s.tag.tolist(),s.home_dir.tolist()))
        mac             =   [int(str(get_mac()))]
        worker          =   s[ s.mac.isin(mac) & s.home_dir.isin([os_environ['HOME']]) ].iloc[0].to_dict()
        self.worker     =   worker['server']
        THIS_SERVER     =   self.worker
        self.base_dir   =   worker['home_dir']
        self.server_idx =   worker['server_idx']
        rank            =   {'high':3,'medium':2,'low':1,'none':0}
        s['ranking']    =   s.production_usage.map(rank)
        self.priority   =   dict(zip(s.tag.tolist(),s.ranking.tolist()))
        local           =   True
        if local   == True:
            self.T      =   self.L


    def mnt_shares(self,folders=[''],local=True):

        if local   == False:
            self.T          =       self.R

        if   folders       ==       ['all']:            folders = T.keys()
        elif folders       ==       ['']:               folders = [self.worker]

        if   folders       ==       ['ub1']:            folders = ['ub2','mbp2']
        elif folders       ==       ['ub2']:            folders = ['mbp2','ub1']
        elif folders       ==       ['mbp2']:           folders = ['ub1','ub2','serv']
        folders             =       [it for it in folders if it!=self.worker]

        p                   =       sub_popen(['ps','-axww'],stdout=sub_PIPE)
        (ap, err)           =       p.communicate()

        for it in folders:
            sshfs           =       os_environ['SSHFS']+' '
            mnt_loc         =       self.T[it]
            if len(re_findall(mnt_loc,ap))==0:
                try:                os_mkdir('/Volumes/'+it)
                except:             pass

                cmd         =       sshfs+mnt_loc+' /Volumes/'+it+' -o ConnectTimeout=5'

                try:
                    proc    =       sub_check_output(cmd, shell=True)
                except:
                    try:            os_rmdir('/Volumes/'+it)
                    except:         pass

        return True
    def umnt_shares(self,folders=['all'],local=True):

        if folders  == ['all']:                 folders = self.T.keys()
        elif folders==['mnt_s1_always']:        folders = ['ub2','mbp2']
        elif folders==['mnt_s2_always']:        folders = ['mbp2','ub1']
        elif folders==['mnt_s3_always']:        folders = ['ub2','ub1']

        folders             =   [it for it in folders if it!=self.worker]
        for it in folders:

            cmd             =   'ps -A | grep ssh | grep -v grep | awk '+"'{print $5}'"
            p               =   sub_popen([cmd], stdout=sub_PIPE, shell=True)
            (t, err)        =   p.communicate()
            chk             =   t.split('\n')

            if chk.count(self.T[it])!=0:
                cmd         =   ['umount /Volumes/%s && rmdir /Volumes/%s'%(it,it)]
                proc        =   sub_popen(cmd, stdout=sub_PIPE, shell=True)
                (t, err)    =   proc.communicate()
                delay(3)

        return True
    def make_display_check(self,system):
        # if   system=='mbp2':
        #     PROC = self.mbp2
        # elif system=='ub1':
        #     PROC = self.ub1
        # elif system=='ub2':
        #     PROC = self.ub2
        #
        # res = []
        # p = sub_popen(["ps", "axw"],stdout=sub_PIPE)
        # (active_processes, err)    =   p.communicate()
        # for k,v in PROC.iteritems():
        #     if re_search(active_processes, v):
        #         res.append(" $(tput bold && tput setaf 1) %s"%k)
        #     else:
        #         res.append("$(tput bold && tput setaf 2) %s"%k)
        # print ';'.join(res)
        pass

class System_Admin:

    def __init__(self):
        s                       =   System_Servers()
        self.servers            =   s.servers
        self.worker             =   s.worker
        self.base_dir           =   s.base_dir
        self.priority           =   s.priority
        self.ready              =   s.mnt_shares(['ub2','ub1','ub3'])
        # self.cfg               =   self.get_cfg()
        self.params             =   {}
        # self.dry_run           =   True
        self.dry_run            =   False
        self.pb                 =   PasteBin().pb

    def get_cfg(self):
        base            = self.base_dir if self.worker=='ub2' else '/Volumes/ub2'+self.base_dir
        cfg_fpath       = base + '/BD_Scripts/files_folders/rsync/backup_system_config.xlsx'
        cfg             = pd.read_excel(cfg_fpath, na_values ='', keep_default_na=False, convert_float=False)
        cols            = cfg.columns.tolist()
        cols_lower      = [str(it).lower() for it in cols]
        cfg.columns     = [cols_lower]
        for it in cols_lower:
            cfg[it]     = cfg[it].map(lambda s: '' if str(s).lower()=='nan' else s)
        tbl             = 'config_rsync'
        conn.set_isolation_level(0)
        cur.execute('drop table if exists %s'%tbl)
        cfg.to_sql(tbl,sys_eng,index=False)
        return cfg

    def add_options(self):
        options         = [ 'verbose','verbose','recursive','archive','update','one-file-system',
                            'compress','prune-empty-dirs','itemize-changes']
                            #,"filter='dir-merge /.rsync-filter'"]
			    # ,'delete-before'
        if self.dry_run==True:      options.append('dry-run')
        self.params.update( { 'options'     :   map(lambda s: '--%s'%s,options) })

    def add_exclusions(self):
        exclude         = self.cfg.exclude.map(lambda s: '--exclude='+str(s)).tolist()
        if len(exclude)!=0:
            self.params.update( { 'exclusions':   exclude, })

    def add_inclusions(self):
        include         = self.cfg.include.map(lambda s: '--include='+str(s)).tolist()
        if len(include)!=0:
            self.params.update( { 'inclusions':   include, })

    def add_logging(self):
        self.params.update( { 'logging'     :   ['--outbuf=L'], })

    def backup_ipython(self,params=''):
        self.process    = 'backup_ipython'
        self.process_start = dt.isoformat(dt.now())
        self.add_options()
        self.add_exclusions()
        from_dir        = '/home/ub2/BD_Scripts/ipython'
        to_dir          = '/home/ub2/'
        src             = from_dir if self.worker=='ub2' else '/Volumes/ub2'+from_dir
        dest            = to_dir   if self.worker=='ub2' else '/Volumes/ub2'+to_dir
        self.params.update( {'src_dir'      :   src,
                             'dest_dir'     :   dest,
                             'operation'    :   '%s: %s'%(self.worker,self.process)})
        self.run_rsync()
        self.process_end = dt.isoformat(dt.now())
        return self.to_pastebin()

    def backup_databases(self,params=''):
        self.process        =   'backup_databases'
        self.process_start  =   dt.isoformat(dt.now())
        T                   =   {'operation'    :   '%s: %s'%(self.worker,self.process)}
        d                   =   System_Databases()
        self.databases      =   d.databases
        self.database_names =   self.databases.db_name.tolist()
        for i in range(len(self.databases)):
            db_info         =   self.databases.ix[i,['backup_path','db_server','db_name','backup_cmd']].map(str)
            fpath           =   '%s/%s_%s_%s.sql'%tuple(db_info[:-1].tolist() + [dt.strftime(dt.now(),'%Y_%m_%d')])
            fname           =   fpath[fpath.rfind('/')+1:]
            cmd             =   """%s -d %s -h 0.0.0.0 -p 8800 --username=postgres > %s
                                """.replace('\n','').replace('\t','').strip()%(db_info['backup_cmd'],db_info['db_name'],fpath)
            if db_info['db_server']!=self.worker:
                cmd         =   "ssh %s '"%db_info['db_server'] + cmd + "'"
            T.update(           {'started'      :   dt.isoformat(dt.now()),
                                 'parameters'   :   cmd.replace("'","''"),} )
            proc            =   sub_popen([cmd], stdout=sub_PIPE, shell=True)
            (t, err)        =   proc.communicate()
            T.update(           {'stout'        :   t,
                                 'sterr'        :   err,
                                 'ended'        :   dt.isoformat(dt.now())} )
            c               =   """insert into system_log values ('%(operation)s','%(started)s',
                                                          '%(parameters)s','%(stout)s',
                                                          '%(sterr)s','%(ended)s')"""%T
            conn.set_isolation_level(0)
            cur.execute(c)

        self.process_end = dt.isoformat(dt.now())
        return self.to_pastebin(params='\n'.join(self.database_names))

    def backup_system(self,params=''):
        self.cfg                =   self.get_cfg()
        self.process            =   'backup_system'
        self.process_start      =   dt.isoformat(dt.now())
        self.add_options()
        self.add_exclusions()       # DON'T ADD INCLUSIONS -- see sync_items below
        cfg                     =   self.cfg
        cols                    =   cfg.columns.map(str).tolist()
        t_cols                  =   [it for it in cols if it[0].isdigit()]

        grps,pt                 =   [],0
        for i in range(len(t_cols)/2):
            x                   =   cfg[[t_cols[pt],t_cols[pt+1],'include']].apply(lambda s: [str(s[0])+'-'+str(s[1]),str(s[2])],axis=1).tolist()
            grps.extend(            x   )
            pt                 +=   2
        res                     =   [it for it in grps if (str(it).find("['-',")==-1 and str(it).find("'']")==-1) ]
        d                       =   pd.DataFrame({ 'server_pair':map(lambda s: s[0],res),
                                                    'transfer_files':map(lambda s: s[1],res)})
        _iters                  =   d.server_pair.unique().tolist()
        for pair in _iters:
            sync_items          =   d[d.server_pair==pair].transfer_files
            incl                =   sync_items.map(lambda s: ' --include='+s).tolist()
            a,b                 =   pair.split('-')
            a_serv,b_serv       =   map(lambda s: str(self.servers[self.servers.tag==s].server.iloc[0]),pair.split('-'))
            a_dir,b_dir         =   map(lambda s: str(self.servers[self.servers.tag==s].home_dir.iloc[0]),pair.split('-'))
            # _host             =    b if priority[a]>priority[b] else a
            src                 =   a_dir if a_serv==self.worker else '/Volumes/'+a_serv+a_dir
            dest                =   b_dir if b_serv==self.worker else '/Volumes/'+b_serv+b_dir
            for it in sync_items:
                self.params.update( {'src_dir'      :   src+'/'+it.lstrip('/'),
                                     'dest_dir'     :   dest+'/',
                                     'operation'    :   '%s: %s -- %s -- %s'%(self.worker,self.process,pair,it)})
                self.run_rsync()
        self.process_end        =   dt.isoformat(dt.now())
        return self.to_pastebin()

    def backup_pip(self,*vars):

        if len(vars)==1:
            single_serv,spec_lib=   True,False
            single_serv_tag     =   vars[0]
        elif len(vars)>1:
            single_serv,spec_lib=   True,True
            single_serv_tag     =   vars[0]
            spec_lib_list       =   vars[1:]
        else:
            single_serv,spec_lib=   False,False


        self.process            =   'backup_pip'
        self.process_start      =   dt.isoformat(dt.now())

        for serv in self.servers.tag.tolist():

            D,old_reqs          =   {},[]


            if single_serv:
                serv            =   single_serv_tag

            libs,save_libs  =   {},{}
            if spec_lib:
                all_libs        =   self.servers[ self.servers.tag==serv ].pip_libs.tolist()[0]
                for it in all_libs.keys():
                    if spec_lib_list.count(it)>0:
                        libs.update({ it                :   all_libs[it] }  )
                    else:
                        save_libs.update({ it           :   all_libs[it] }  )
            else:
                libs            =   self.servers[ self.servers.tag==serv ].pip_libs.tolist()[0]


            for k,v in libs.iteritems():

                # print serv,k

                if v['requirements']!='':
                    old_reqs.append(v['requirements'].replace('http://pastebin.com/','')  )

                lib_loc         =   v['location']
                cmds            =   ['cd %s' % lib_loc]
                if lib_loc.find('ENV')>0:
                    cmds.append(    'source bin/activate'  )
                cmds.append(        'pip freeze'  )

                cmd             =   '; '.join(cmds)
                if serv!=self.worker:
                    cmd         =   "ssh %s '%s'" % (serv,cmd)

                proc            =   sub_check_output(cmd, stderr=sub_stdout, shell=True)

                pb_url          =   self.pb.createPaste(  proc,
                                        api_paste_name='%s -- pip_lib: %s' % (serv,k),
                                        api_paste_format='',
                                        api_paste_private='1',
                                        api_paste_expire_date='N')

                D.update(           { k     :   {'location'     :   lib_loc,
                                                 'requirements' :   pb_url }
                                    })

            # Append any libs not updated
            for k,v in save_libs.iteritems():
                D.update(           { k     :   v }  )

            # Push to servers DB
            cmd                 =   """
                                        UPDATE servers SET
                                        pip_libs            =   '%s',
                                        pip_last_updated    =   'now'::timestamp with time zone
                                        WHERE tag = '%s'
                                    """ % (j_dump(D),serv)

            conn.set_isolation_level(0)
            cur.execute(            cmd   )

            # Delete old Pastes
            for it in old_reqs:
                self.pb.deletePaste(it)

            if single_serv:
                break


        self.process_end        =   dt.isoformat(dt.now())
        return

    def to_pastebin(self,params=''):
        if self.dry_run==True:      return True
        else:

            condition           =   """
                                        operation ilike '%s: %s%s'
                                        and started >=  '%s'::timestamp with time zone
                                        and ended   <  '%s'::timestamp with time zone
                                    """ % (self.worker,self.process,'%%',
                                           self.process_start,self.process_end)

            df                  =   pd.read_sql("select * from system_log where %s" % condition,sys_eng)

            T                   =   df.iloc[0].to_dict()
            T['operation']      =   '%s: %s' % (self.worker,self.process)
            pb_url              =   self.pb.createPaste(df.to_html(), api_paste_name = T['operation'],
                                                      api_paste_format = 'html5', api_paste_private = '1',
                                                      api_paste_expire_date = '2W')

            T['stout']          =   pb_url
            T['ended']          =   dt.isoformat(dt.now())
            T['parameters']     =   '\n\n'.join(df.parameters.tolist()).replace("'","''")
            c                   =   """insert into system_log values ('%(operation)s','%(started)s',
                                                              '%(parameters)s','%(stout)s',
                                                              '%(sterr)s','%(ended)s')"""%T
            conn.set_isolation_level(0)
            cur.execute(            c   )

            conn.set_isolation_level(0)
            cur.execute(            "delete from system_log where %s " % condition  )
            return True

    def run_rsync(self):
        c,keys              =   ['rsync'],self.params.keys()
        if keys.count('options'):               c.extend(self.params['options'])
        if keys.count('inclusions'):            c.extend(self.params['inclusions'])
        if keys.count('exclusions'):            c.extend(self.params['exclusions'])
        if keys.count('logging'):               c.extend(self.params['logging'])

        c.extend([      self.params['src_dir'], self.params['dest_dir'] ])
        cmd                 =   ' '.join(c)
        start_ts            =   dt.isoformat(dt.now())
        proc                =   sub_popen([cmd], stdout=sub_PIPE, shell=True)
        (t, err)            =   proc.communicate()
        c                   =   "insert into system_log values ('%s','%s','%s','%s','%s','%s')"%(
                                self.params['operation'],start_ts,
                                '%s %s'%(self.params['src_dir'],self.params['dest_dir']),
                                unicode(t).replace("'","''"), unicode(err).replace("'","''"), dt.isoformat(dt.now()))
        conn.set_isolation_level(0)
        cur.execute(c)
        return True



from sys import argv
if __name__ == '__main__':
    if len(argv)>1:

        if argv[1].find('backup_')==0:
            SYS = System_Admin()
            if (len(argv)>2 and argv[2]=='dry-run'):
                SYS.dry_run     =   True
            elif len(argv)>2:
                vars            =   argv[2:]
            else:
                vars            =   []


            if  argv[1]=='backup_all':
                SYS.backup_ipython()
                SYS.backup_databases()
                SYS.backup_system()
                SYS.backup_pip()


            elif  argv[1]=='backup_ipython':     SYS.backup_ipython()
            elif  argv[1]=='backup_databases':   SYS.backup_databases()
            elif  argv[1]=='backup_system':      SYS.backup_system()
            elif  argv[1]=='backup_pip':         SYS.backup_pip(*vars)

        elif argv[1]=='check_health':
            SYS             =       System_Health()
            SYS.make_display_check(argv[2])

        elif argv[1]=='cron':
            CRON = System_Crons()
            if   argv[2]=='logrotate':
                CRON.check_log_rotate()
            elif argv[2]=='git_fsck':
                CRON.run_git_fsck()