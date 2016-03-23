

def main(args,kwargs):
    if args.count('requests'):              import requests
    if args.count('urllib'):                from urllib import quote_plus,unquote

    import                                  datetime                as DT
    import                                  time
    delay                                   =   time.sleep
    from dateutil                           import parser           as DU               # e.g., DU.parse('some date as str') --> obj(datetime.datetime)
    from re                                 import findall          as re_findall
    from re                                 import sub              as re_sub           # re_sub('patt','repl','str','cnt')
    from re                                 import search           as re_search        # re_search('patt','str')
    import json
    from subprocess                         import Popen            as sub_popen
    from subprocess                         import PIPE             as sub_PIPE
    from traceback                          import format_exc       as tb_format_exc
    from sys                                import exc_info         as sys_exc_info
    from types                              import NoneType
    from uuid                               import uuid4            as get_guid
    from py_classes                         import To_Class,To_Class_Dict,To_Sub_Classes
    import                                  pandas                  as pd
    pd.set_option(                          'expand_frame_repr', False)
    pd.set_option(                          'display.max_columns', None)
    pd.set_option(                          'display.max_colwidth', 250)
    pd.set_option(                          'display.max_rows', 1000)
    pd.set_option(                          'display.width', 1500)
    pd.set_option(                          'display.colheader_justify','left')
    np                                      =   pd.np
    np.set_printoptions(                    linewidth=1500,threshold=np.nan)
    import logging
    logger = logging.getLogger(             'sqlalchemy.dialects.postgresql')
    logger.setLevel(logging.INFO)

    if args.count('pgsql'):              
        from sqlalchemy                     import create_engine
        from psycopg2                       import connect          as pg_connect
        try:
            eng                             =   create_engine(r'postgresql://%(DB_USER)s:%(DB_PW)s@%(DB_HOST)s:%(DB_PORT)s/%(DB_NAME)s'
                                                              % self.T.pgsql,
                                                              encoding='utf-8',
                                                              echo=False)
            conn                            =   pg_connect("dbname='%(DB_NAME)s' host='%(DB_HOST)s' port=%(DB_PORT)s \
                                                           user='%(DB_USER)s' password='%(DB_PW)s' "
                                                           % self.T.pgsql);
            cur                             =   conn.cursor()

        except:
            from getpass import getpass
            pw = getpass('Root password (to create DB:"%(DB_NAME)s" via CL): ' % self.T.pgsql)
            p = sub_popen(" ".join(["echo '%s' | sudo -S prompt='' " % pw,
                                    'su postgres -c "psql --cluster 9.4/main -c ',
                                    "'create database %(DB_NAME)s;'" % self.T.pgsql,
                                    '"']),
                          stdout=sub_PIPE,
                          shell=True)
            (_out, _err) = p.communicate()
            assert _err is None

    import inspect, os
    D                                       =   {'guid'                 :   str(get_guid().hex)[:7],
                                                 'pg_classes_pwd'       :   os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))),
                                                }
    D.update(                                   {'tmp_tbl'              :   'tmp_'+D['guid'],
                                                'current_filepath'     :   inspect.getfile(inspect.currentframe())})



    T                                       =   To_Class_Dict(  self,
                                                            dict_list=[D,locals()],
                                                            update_globals=True)    