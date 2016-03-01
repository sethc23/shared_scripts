from selenium                       import webdriver
from time                           import sleep
from bs4                            import BeautifulSoup        as BS
import                                  pandas                  as pd
from sqlalchemy                     import create_engine
from system_settings                import DB_HOST,DB_PORT
from subprocess                     import Popen                as sub_popen
from subprocess                     import PIPE                 as sub_PIPE

D                                   =   webdriver.PhantomJS(executable_path='/usr/local/bin/phantomjs')
D.set_window_position(                  0, 0)
D.set_window_size(                      300, 300)
capabilities                        =   ['applicationCacheEnabled',
                                         'locationContextEnabled',
                                         'databaseEnabled',
                                         'webStorageEnabled',
                                         'JavascriptEnabled',
                                         'acceptSslCerts',
                                         'browserConnectionEnabled',
                                         'rotatable']
for it in capabilities:
    D.desired_capabilities[it]      =   True
username,pw                         =   'sethc23','ferrarif50'
login                               =   'https://github.com/session'
homepage                            =   'https://github.com/sethc23'
D.get(                                  login)
D.find_element_by_id("login_field").send_keys(  username)
D.find_element_by_id("password").send_keys(     pw)
D.find_element_by_name("commit").click(         )
D.implicitly_wait(                      60)
D.get(                                  homepage)

sleep(                                  10)
D.get(                                  homepage)
src                                 =   D.page_source
D.quit()

h                                   =   BS(src)
t                                   =   h.findAll('svg',attrs={'class':"js-calendar-graph-svg"})[0]
x                                   =   str(t).replace('\n','')

repl                                =   {'fill="#eeeeee"'               :   'opacity="0.25" fill="#eeeeee"',
                                         # light to dark
                                         '1e6823'                       :   '7FFF00',
                                         '44a340'                       :   '00FF7F',
                                         '8cc665'                       :   '32CD32',
                                         'd6e685'                       :   '228B22'}
for k,v in repl.iteritems():
    x                               =   x.replace(k,v)

t                                   =   x.find('data-date')+11
st_date                             =   x[t:t+10]

t                                   =   x.rfind('data-date')+11
end_date                            =   x[t:t+10]

conn                                =   create_engine(r'postgresql://postgres:postgres@%s:%s/seth' % (DB_HOST,DB_PORT),
                                                       encoding='utf-8',
                                                       echo=False)
q                                   =   """
                                        select to_char(attendance_date,'YYYY-MM-DD') date,lift,cardio
                                        from gym
                                        where attendance_date between date '%(st_date)s'
                                        and (date '%(end_date)s' + time '23:59')
                                        order by attendance_date asc
                                        """ % {'st_date':st_date,'end_date':end_date}
df                                  =   pd.read_sql(q,conn)

colors                              =   {'cardio'                       :   '#FFFC00;stroke-width:3.5;',
                                         'lift'                         :   '#7CFFFF;stroke-width:3.5;',
                                         'lift_and_cardio'              :   '#FF0090;stroke-width:3.5;'}
z                                   =   df.date.tolist()
for i in range(len(z)):
    it                              =   z[i]
    s                               =   x.find(it)
    e                               =   x[s:].find('>')
    txt                             =   x[s:s+e]
    s                               =   txt.find('fill')
    e                               =   txt[s+6:].find('"')+1
    repl                            =   txt[s:s+6+e]
    new                             =   txt.replace(repl,'style="%s;stroke:TMP"'%repl.replace('=',':').replace('"',''))
    lift                            =   df.ix[i,'lift']
    cardio                          =   df.ix[i,'cardio']
    if lift == True and cardio == True:
        repl_color                  =   colors['lift_and_cardio']
        new                         =   new.replace('TMP',repl_color)
        x                           =   x.replace(txt,new)
    elif lift == True:
        repl_color                  =   colors['lift']
        new                         =   new.replace('TMP',repl_color)
        x                           =   x.replace(txt,new)
    elif cardio == True:
        repl_color                  =   colors['cardio']
        new                         =   new.replace('TMP',repl_color)
        x                           =   x.replace(txt,new)

repl                                =   {'text-anchor="middle"'         :   'fill="#00FFFF" text-anchor="middle"',
                                         'class="month"'                :   'fill="#00FFFF"',}
for k,v in repl.iteritems():
    x                               =   x.replace(k,v)
tmp_f_path                          =   'files/tmp.txt'
with open(tmp_f_path,'w') as f:         f.write(x)
# from subprocess import check_output as sub_check_output
# proc=sub_check_output('echo `cat files/tmp.txt` | cairosvg - -f png -o files/git_commits.png', shell=True)

cmd                                 =   '; '.join(
                                        ['echo `cat %s` | cairosvg - -f png -o files/git_commits.png' % tmp_f_path,
                                         'rm -f %s' % tmp_f_path,]
                                                )
p                                   =   sub_popen(cmd,stdout=sub_PIPE,shell=True)
(_out,_err)                         =   p.communicate()
assert _err                        ==   None