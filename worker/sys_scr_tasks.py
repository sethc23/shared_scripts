from os                                     import environ                      as os_environ
from sys                                    import path                         as py_path
py_path.append(                                 os_environ['HOME'] + '/.scripts')
from system_settings                        import *

from os                                     import system                       as os_cmd
from celery                                 import task#,shared_task
# from os                                     import path                         as os_path

# from datetime                               import datetime                     as dt
# import requests
# from json                                   import dumps                        as j_dumps
# from bs4                                    import BeautifulSoup                as soup
# from re                                     import findall                      as re_findall
# from re                                     import sub                          as re_sub
#
# from pandas                                 import DataFrame                    as pd_DataFrame
# from pandas                                 import read_sql                     as pd_read_sql
from sqlalchemy                             import create_engine
from psycopg2                               import connect                      as psycopg2_connect

# from codecs import encode as codecs_encode
# import sys
# reload(sys)
# sys.setdefaultencoding('UTF8')


# ----------------------------------------- <<
# ----------------------------------------- <<
# Using this segment to Setup one DB Connection per Worker
# ----------------------------------------- <<

from celery.signals                         import worker_process_init,worker_process_shutdown

sys_conn                                    =   None
sys_cur                                     =   None
sys_eng                                     =   None

@worker_process_init.connect
def init_worker(**kwargs):
    global sys_conn,sys_cur,sys_eng
    print(                                      'Initializing database connection for worker.')
    sys_eng                                 =   create_engine(r'postgresql://postgres:postgres@%s:%s/%s'
                                                                %(DB_HOST,DB_PORT,DB_NAME),
                                                                encoding='utf-8',echo=False)
    sys_conn                                =   psycopg2_connect(""" dbname='%s' user='postgres'
                                                                     host='%s' password='' port=%s
                                                                 """%(DB_NAME,DB_HOST,DB_PORT))
    sys_cur                                 =   sys_conn.cursor()

@worker_process_shutdown.connect
def shutdown_worker(**kwargs):
    global sys_conn,sys_cur,sys_eng
    if sys_conn:
        print(                                  'Closing database connection for worker.')
        sys_conn.close(                         )
    if sys_eng:
        print(                                  'Closing database connection for worker.')
        sys_eng.dispose(                        )

# ----------------------------------------- >>
# ----------------------------------------- >>

####
##
"""
    Task Options:

    @shared_task
        ignore_result
        store_errors_even_if_ignored

"""
##
####

@task
def pgsql_query(qry=None):
    os_cmd(                                 "logger -t 'sys_scr' '%s'" % str(qry))

    return "result"
