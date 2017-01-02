import                                  os,hashlib,re,json,calendar
from types                              import NoneType
from uuid                               import uuid4 as uuid
import                                  datetime as DT
import                                  pandas as pd
pd.set_option(                          'expand_frame_repr',False)
pd.set_option(                          'display.max_columns', None)
pd.set_option(                          'display.max_rows', 1000)
pd.set_option(                          'display.width',180)
np                              =       pd.np
np.set_printoptions(                    linewidth=200,threshold=np.nan)
from subprocess                         import Popen as sub_popen
from subprocess                         import PIPE as sub_PIPE

# from sqlalchemy                         import create_engine
# import                                  logging
# logging.basicConfig()
# logging.getLogger(                      'sqlalchemy.engine').setLevel(logging.WARNING)
# from psycopg2                           import connect as pg_connect

# T = {'DB_NAME':'fileserver',
#      'DB_HOST':'0.0.0.0',
#      'DB_PORT':'8800',
#      'DB_USER':'postgres',
#      'DB_PW':''}

# def _load_connectors():
#     eng                         =   create_engine(r'postgresql://%(DB_USER)s:%(DB_PW)s@%(DB_HOST)s:%(DB_PORT)s/%(DB_NAME)s'
#                                                   % T,
#                                                   encoding='utf-8',
#                                                   echo=False)
#     conn                        =   pg_connect("""dbname='%(DB_NAME)s' host='%(DB_HOST)s' port=%(DB_PORT)s
#                                                user='%(DB_USER)s' password='%(DB_PW)s' """
#                                                % T);
#     cur                         =   conn.cursor()
#     return eng,conn,cur


# try:
#     eng,conn,cur            =   _load_connectors()
# except:
#     from getpass                import getpass
#     pw = getpass('Root password (to create DB:"%(DB_NAME)s" via CL): ' % T)
#     p = sub_popen(" ".join(["echo '%s' | sudo -S prompt='' " % pw,
#                             'su postgres -c "psql --cluster 9.4/main -c ',
#                             "'create database %(DB_NAME)s;'" % T,
#                             '"']),
#                   stdout=sub_PIPE,
#                   shell=True)
#     (_out, _err)            =   p.communicate()
#     assert _err is None
#     eng,conn,cur            =   _load_connectors()


# LINUX REQ'S:
# 	apt-get install -y imagemagick poppler-utils jq libreoffice
# 	cpan -i Email::Outlook::Message
# 	wget http://apache.claz.org/tika/tika-app-1.13.jar
# 	tesseract-ocr tesseract-ocr-eng tesseract-ocr-osd
# 	lynx --> lynx --dump -nomargins -dont_wrap_pre <(cat tmp)
#   mpack --> munpack
#   wkhtmltopdf

# VIRTUAL_ENV='~/.virtualenvs/fileserver'
VIRTUAL_ENV = os.environ['HOME_ENV'] + '/.virtualenvs/dev'
PROJ_HOME = os.environ['HOME_ENV'] + '/PROJECTS/INTARCIA'
WORKING_DIR = PROJ_HOME+'/scripts'
# abs_path = run_cmd("stat -c '%N' "+VIRTUAL_ENV).strip("'")

DOC_SRC_DIR = PROJ_HOME+'/AGREEMENTS'
DOC_DEST_DIR = PROJ_HOME+'/AGREEMENTS_cons'
DOC_RESOURCE_DIR = PROJ_HOME+'/AGREEMENTS_build'
DOC_OCR_DIR = PROJ_HOME+'/AGREEMENTS_ocr'
DOC_CONV_DIR = PROJ_HOME+'/AGREEMENTS_conv'

PYPDFOCR = VIRTUAL_ENV + '/bin/pypdfocr'
TIKA = os.environ['HOME_ENV'] + '/.scripts/toolbox/tika_meta'

FROM_CMD_LINE=True
# App Functions

def run_cmd(cmd):
    p = sub_popen(cmd,stdout=sub_PIPE,shell=True,executable='/bin/zsh')
    (_out,_err) = p.communicate()
    assert _err is None
    return _out.rstrip('\n')

def get_file_list(src_dir,exclude_list=[]):
    file_list = []
    for root, sub_dir, files in os.walk(src_dir):
        for f in files:
            file_list.append({
            'fpath': os.path.join(root,f).replace('\\','/'),
            'fname': f,
            })
    if file_list:
        df = pd.DataFrame(file_list)
        df['fext'] = df.fname.map(lambda s: '' if not s.count('.') else s[s.rfind('.')+1:])
        if len(df[df.fext==''])!=0:
            print("at least one filepath does not have a period")
        return df
    else:
        return False

def get_file_idx_plus(dir_or_dir_list,**kwargs):
    """
        DEFAULTS (can be replaces via kwargs):

            get_md5                 =   True
            get_times               =   True
            enumerate_fname_dupes   =   True
            save_path               =   '/tmp/flist'
            save_type               =   'xls'

    """
    if kwargs:
        locals().update(kwargs)
        globals().update(kwargs)
    get_md5 = True if not kwargs.has_key('get_md5') else kwargs['get_md5']
    get_times = True if not kwargs.has_key('get_times') else kwargs['get_times']
    enumerate_fname_dupes = True if not kwargs.has_key('enumerate_fname_dupes') else kwargs['enumerate_fname_dupes']
    save_path = '/tmp/flist' if not kwargs.has_key('save_path') else kwargs['save_path']
    save_type = 'xls' if not kwargs.has_key('save_type') else kwargs['save_type']

    if not type(dir_or_dir_list)==list:
        dir_or_dir_list = [dir_or_dir_list]
    df = None
    for d in dir_or_dir_list:
        if type(df)==NoneType:
            df = get_file_list(d)
        else:
            nf = get_file_list(d)
            df = df.append(nf,ignore_index=True)
    if get_md5:
        df['md5'] = df.fpath.map(lambda s: md5(s) )
    if get_times:
        df['f_last_modified'] = df.fpath.map(lambda s: file_attribute(s,'file_mod_epoch'))
        df.f_last_modified=df.f_last_modified.astype(int)
        df['f_created'] = df.fpath.map(lambda s: file_attribute(s,'file_birth_epoch'))
        df.f_created=df.f_created.astype(int)

        df['f_last_modified_2'] = df.fpath.map(lambda s: os.path.getmtime(s) )
        df['f_created_2'] = df.fpath.map(lambda s: os.path.getctime(s) )

    if enumerate_fname_dupes:
        df = get_consolidated_paths_and_enum_dupes(df)

    D = {
        'save_dir'      :   os.path.dirname(save_path),
        'date_time'     :   DT.datetime.now().strftime('%Y.%m.%d'),
        'fname'         :   os.path.basename(save_path),
        'uuid'          :   uuid().hex[:8],
        'ftype'         :   save_type,
        }
    save_fpath = '%(save_dir)s/%(date_time)s_%(fname)s_%(uuid)s.%(ftype)s' % D

    if save_type.count('xls'):
        df.to_excel(save_fpath)
    print 'Saved to:',save_fpath
    return df

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def file_attribute(fpath,attr):
    attr_dict = {
        'access_rights_human': 'A',
        'access_rights_octal': 'a',
        'block_number': 'b',
        'block_size_bytes': 'B',
        'device_decimal': 'd',
        'device_hex': 'D',
        'file_access_epoch': 'X',
        'file_access_human': 'x',
        'file_birth_epoch': 'W',
        'file_birth_human': 'w',
        'file_change_epoch': 'Z',
        'file_change_human': 'z',
        'file_mod_epoch': 'Y',
        'file_mod_human': 'y',
        'file_name': 'n',
        'file_type': 'F',
        'hard_link_number': 'h',
        'inode_number': 'i',
        'major_device_hex': 't',
        'minor_device_hex': 'T',
        'mount_point': 'm',
        'optimal_xfer': 'o',
        'owner_group_ID': 'g',
        'owner_group_name': 'G',
        'owner_user_ID': 'u',
        'owner_user_name': 'U',
        'quoted_file_name': 'N',
        'raw_mode_hex': 'f',
        'SELinux': 'C',
        'total_size_bytes': 's'
         }

    assert attr_dict.keys().count(attr),"Attribute request is not recognized: "+attr
    K=attr_dict[attr]
    return run_cmd("stat -c \"%"+K+"\" \""+fpath.replace('$',r'\$')+"""\"""")

def pdf_slice(fpath_from,pg_start,pg_end,fpath_to,run_ocr=True):
    cmd = """
        cd /tmp;
        rm -fr pdf_slice;
        mkdir pdf_slice;
        cd pdf_slice;
        pdftoppm -f %(pg_start)s -l %(pg_end)s %(fpath_from)s '_ppm_';
        convert ./_ppm_* -page Letter %(fpath_to)s;
        cd ..;
        rm -fr pdf_slice;
        """ % {
            'fpath_from' : fpath_from,
            'pg_start' : pg_start,
            'pg_end' : pg_end,
            'fpath_to' : fpath_to,
            }
    run_cmd(cmd)
    if run_ocr:
        _run_pypdfocr(fpath_to)

def _pdf_to_text(cmd=''):
    # print 'fname:',fname
    # print 'fname_pdf:',fname_pdf
    # print 'fpath:',fpath
    # print 'fpath_pdf:',fpath_pdf
    # print 'fpath_pdf_ocr:',fpath_pdf_ocr
    # print 'DOC_RESOURCE_DIR:',DOC_RESOURCE_DIR
    # print 'DOC_DEST_DIR:',DOC_DEST_DIR
    # print 'DOC_CONV_DIR:',DOC_CONV_DIR
    # print 'fname_gen_dir:',fname_gen_dir

    return cmd + ';\n'.join([
        'convert '+fpath+" -type Grayscale -page Letter '%s'" % fpath_pdf,
        PYPDFOCR + " '%s' > /dev/null 2>&1" % fpath_pdf,
        "pdftotext -q -nopgbrk '%s' -" % fpath_pdf_ocr,
        #"mv "+fpath_pdf+' '+DOC_RESOURCE_DIR+'/'+fpath_pdf,
        "mv "+fpath_pdf_ocr+' '+DOC_RESOURCE_DIR+'/'+fpath_pdf_ocr,
        "mv "+fname_gen_dir+' '+DOC_DEST_DIR+'/'+fname_pdf,
        "mv "+fpath+' '+DOC_CONV_DIR+'/'+fname,
        ]) + ';\n'
def _run_pypdfocr(fpath,virtual_env='/home/kali/.virtualenvs/dev',replace_orig=True):
    fdir = os.path.dirname(fpath)
    fname = os.path.basename(fpath)
    fpath_pdf_ocr = '%s_ocr.pdf' % fname[:-4]
    run_cmd(
        ';\n'.join([
                'cd "%s"' % fdir,
                'source "%s/bin/activate"' % virtual_env,
                'pypdfocr "%s"' % fpath
            ]) + ';\n'
        )
    if replace_orig:
        run_cmd(
        ';\n'.join([
                'cd "%s"' % fdir,
                'mv %s %s' % (fpath_pdf_ocr,fpath),
            ]) + ';\n'
        )
def _pdf_has_text():
    c = ';\n'.join([
            'cd '+fpath[:fpath.rfind('/')],
            "pdftotext -q -nopgbrk '%s' -" % fpath_pdf_ocr,
            ])
    chk = run_cmd(c)
    print 'chk:',chk
    print 'len:',len(chk)
    return True if len(chk) else False

def redo_pdf_ocr(fpath):
    cmd = """
        PREFIX="_ppm_"
        SRC="/tmp/pdf_to_do"
        source ~/.virtualenvs/dev/bin/activate
        cd /home/kali/PROJECTS/INTARCIA/AGREEMENTS_ocr
        for i in $(cat $SRC); do
            BASE_DIR=${i:a:h}
            FNAME=$(echo $i|sed -r 's/(.*)\/([^/]+)$/\2/')
            BASE_FNAME=$(echo "$FNAME"|sed 's/\.pdf//')
            NEW_PDF=$FNAME
            NEW_OCR=$BASE_FNAME"_ocr.pdf"
            /usr/bin/pdftoppm $i $PREFIX
          /usr/bin/convert $(env ls -1|env grep -E \^"$PREFIX") -type Grayscale -page Letter "$NEW_PDF"
          ~/.virtualenvs/dev/bin/python /home/kali/.virtualenvs/dev/bin/pypdfocr "$NEW_PDF"
          rm ./$PREFIX*
          rm $NEW_PDF
          cat $SRC | grep -v $i > /tmp/src
          cat /tmp/src > $SRC
        done
        """
    D = {
        'fpath' : fpath
        ,'fname' : os.path.basename
        }
    cmd = """
        PREFIX="_ppm_"
        source ~/.virtualenvs/dev/bin/activate

        FNAME="%(fname)s"
        BASE_FNAME=$(echo "$FNAME"|sed 's/\.pdf//')
        NEW_PDF=$BASE_FNAME"_reocr.pdf"
        NEW_OCR=$BASE_FNAME"_ocr.pdf"

        pdftoppm $%(fpath)s $PREFIX
        convert $(env ls -1|env grep -E \^"$PREFIX") -type Grayscale -page Letter "$NEW_PDF"
        pypdfocr "$NEW_PDF"
        rm ./$PREFIX*
        #rm $NEW_PDF

        """ % D
    run_cmd(cmd)

def file_info(fpath,info_type,FROM_CMD_LINE=True):
    def pdf_to_text(cmd=''):
        print 'fname:',fname
        print 'fname_pdf:',fname_pdf
        print 'fpath:',fpath
        print 'fpath_pdf:',fpath_pdf
        print 'fpath_pdf_ocr:',fpath_pdf_ocr
        print 'fname_gen_dir:',fname_gen_dir
        print 'DOC_RESOURCE_DIR:',DOC_RESOURCE_DIR
        print 'DOC_DEST_DIR:',DOC_DEST_DIR
        print 'DOC_CONV_DIR:',DOC_CONV_DIR

        # return cmd + ';\n'.join([
        #     'convert '+fpath+" -type Grayscale -page Letter '%s'" % fpath_pdf,
        #     PYPDFOCR + " '%s' > /dev/null 2>&1" % fpath_pdf,
        #     "pdftotext -q -nopgbrk '%s' -" % fpath_pdf_ocr,
        #     #"mv "+fpath_pdf+' '+DOC_RESOURCE_DIR+'/'+fpath_pdf,
        #     "mv "+fpath_pdf_ocr+' '+DOC_RESOURCE_DIR+'/'+fpath_pdf_ocr,
        #     "mv "+fname_gen_dir+' '+DOC_DEST_DIR+'/'+fname_pdf,
        #     "mv "+fpath+' '+DOC_CONV_DIR+'/'+fname,
        #     ]) + ';\n'
    def mv_orig_and_rename_converted(cmd=''):
        return cmd + ';\n'.join([
            "mv "+fpath+' '+DOC_CONV_DIR+'/'+fname,
            "mv "+fname_gen_dir+' '+fpath_dir+'/'+fname_pdf,
            ]) + ';\n'
    def run_pypdfocr(cmd='',replace_orig=True):
        run_cmd(
            ';\n'.join([
                    'cd "%s"' % PROJ_HOME,
                    'source "%s/bin/activate"' % VIRTUAL_ENV,
                    'pypdfocr "%s"' % fpath
                ]) + ';\n'
            )
        if replace_orig:
            run_cmd('mv %s %s' % (fpath_pdf_ocr,fpath))
    def pdf_has_text():
        c = ';\n'.join([
                'cd '+fpath[:fpath.rfind('/')],
                "pdftotext -q -nopgbrk '%s' -" % fpath_pdf_ocr,
                ])
        chk = run_cmd(c)
        print 'chk:',chk
        print 'len:',len(chk)
        return True if len(chk) else False



    fname = fpath[fpath.rfind('/')+1:]
    assert fname[0]!='.',"ERROR: file info not configured to handle files without typical 'filename.ext' format"
    fname_base = fname[:fname.rfind('.')]
    INFO_TYPES = ['metadata','text','html_text']
    MS_EXTS = ['doc','docx','docm','ppt','pptx','xls','xlsx']
    OTHER_EXTS = ['bmp','msg','pdf']
    EXTS = MS_EXTS + OTHER_EXTS

    assert INFO_TYPES.count(info_type),'Unknown info_type: '+info_type
    f_ext = fpath[fpath.rfind('.')+1:]
    assert EXTS.count(f_ext),'Unknown fpath extension: '+f_ext

    fname_gen = '%s.pdf' % fname_base
    fname_pdf =  '%s.pdf' % fname

    fpath_dir = fpath[:fpath.rfind('/')]
    fpath_pdf = '%s.pdf' % fpath

    fname_gen_dir = fpath_dir + '/' + fname_gen

    fpath_pdf = '%s.pdf'%fpath[:fpath.rfind('.')]
    fpath_pdf_ocr = '%s_ocr.pdf'%fpath[:fpath.rfind('.')]

    if info_type=='metadata':
        # cmd="""\
        #         pdfinfo -meta %s | \
        #         jq -s -R -c -M -j \
        #         '[ splits("\n")? | split(":") as $i | { ($i[0]?) : ( $i[1] | sub("( )+"; ""; "sl") ) } ]'\
        #         """ % fpath
        print 'tike emta'
        cmd = TIKA + " '%s'" % fpath

    elif info_type=='text':
        if f_ext=='bmp':
            cmd = ';\n'.join([
                'convert '+fpath+" -type Grayscale -page Letter '%s'" % fpath_pdf,
                PYPDFOCR + " '%s' > /dev/null 2>&1" % fpath_pdf,
                ]) + ';\n'
            cmd = pdf_to_text(cmd)
        elif f_ext=='msg':
            # converting 'msg' (where `file <filename>.msg`='Composite Document File V2 Document')
            #   --> Run: `cpan -i Email::Outlook::Message`
            #   --> Usage: msgconvert <fpath>
            cmd = ';\n'.join([
                    'rm -fr ./tmp_eml',
                    'mkdir -p ./tmp_eml; cd ./tmp_eml',
                    'msgconvert '+fpath,
                    'EMAIL_PATH=$(env ls -1|head -n 1)',
                    'mkdir -p ./tmp_parts; cd ./tmp_parts',
                    'munpack -q -t ../$EMAIL_PATH > /dev/null 2>&1',
                    '; '.join([
                        'for i in $(env ls -1)',
                        """do [[ -n "$(file ./$i|grep 'text,')" ]] && cat ./$i >> ../$EMAIL_PATH""",
                        'done'
                        ]),
                    'cat "../$EMAIL_PATH"',
                    'cd ../..; rm -fr ./tmp_eml',
                    ])
        elif f_ext=='pdf':
            # CONFIRM PDFTOTEXT EXISTS
            if not pdf_has_text():
                run_pypdfocr(replace_orig=True)
            if not pdf_has_text():
                print 'still no text:',fpath
                raise SystemError
            cmd="""lynx --dump -nomargins -dont_wrap_pre \
                    <(pdftotext -q -nopgbrk %s -)""" % fpath
        elif MS_EXTS.count(f_ext):
            cmd = ';\n'.join([
                "libreoffice --headless --invisible --convert-to pdf '"+fpath+"' --outdir "+fpath_dir+" >/dev/null 2>&1",
                "rm -fr missfont.log",
                ]) + ';'
            cmd = mv_orig_and_rename_converted(cmd)
        else:
            print('unknown file to be gotten')
            raise SystemError

    elif info_type=='html_text':
        print 'not configured yet'
        raise SystemError

    res = run_cmd(cmd)
    if FROM_CMD_LINE:
        print res
    return res

def remove_non_ascii(text,repl=' '):
    # [True if ord(c) < 128 else False for c in z].count(False)==0
    return re.sub(r'[^\x00-\x7F]+',repl, text)

def remove_non_alnum(text,repl=' '):
    return re.sub(r'(?iLmsux)[^a-z0-9]+',repl, remove_non_ascii(text,repl)).strip(' _')

def get_consolidated_paths_and_enum_dupes(df=None,consol_dir='AGREEMENTS_cons'):
    #df = pd.read_sql("select * from new_f",eng) if df.__class__.__name__!='DataFrame' else df

    # df['fpath'] = df.fpath.map(lambda s: re.sub(r'^L:\\AGREEMENTS','',s) )
    df['fpath_cons'] = df.fname.map(lambda s: consol_dir+'/'+remove_non_alnum(s[s.rfind('/')+1:],'_'))
    df['fpath_cons'] = df.ix[:,['fpath_cons','fext']].apply(lambda s: s[0][:(-1*len(s[1]))-1] + ".%s" % s[1], axis=1)
    df.fext = df.fext.str.lower()
    all_fpath_cons = df.fpath_cons.tolist()
    df['fpath_cons_cnt'] = df.fpath_cons.map(lambda s: all_fpath_cons.count(s))

    fix = df[df.fpath_cons_cnt!=1].copy()
    fix['f_latest'] = False
    fix = fix.sort_values(['fpath_cons','f_last_modified'],ascending=[True,False])
    grps = fix.groupby('fpath_cons')
    for k,v in grps.groups.iteritems():
        gf = fix.ix[v,:].copy()
        gf = gf.sort_values('f_last_modified',ascending=False)
        ver = ''
        for i,r in gf.iterrows():
            # idx = df[df.uid==r['uid']].index.tolist()
            # assert len(idx)==1
            # idx = idx[0]

            pt = df.iloc[i]
            old_fpath_cons = pt['fpath_cons']
            _pattern = r'(?i)(.*)(\.'+pt['fext']+r')$'
            _repl = r'\1_'+str(ver)+r'\2' if pt['fpath_cons'][0]=='/' else r'\1_/'+str(ver)+r'\2'
            _string = pt['fpath_cons']
            new_fpath_cons = re.sub(_pattern,_repl,_string,count=1)

            df.set_value(i,'fpath_cons',new_fpath_cons)
            ver = 1 if not ver else ver+1
    all_fpath_cons = df.fpath_cons.tolist()
    df['fpath_cons_cnt'] = df.fpath_cons.map(lambda s: all_fpath_cons.count(s))
    df.drop(['fpath_cons_cnt'],axis=1,inplace=True)
    return df

def consolidate_dirs_and_clean_paths(consol_dir='AGREEMENTS_cons',exclude_files=['Thumbs.db','.DS_Store']):
    def clean_workspace():
        run_cmd(';'.join([
            'rm -fr %s'%consol_dir,
            'mkdir -p %s'%consol_dir
            ]))
    def remove_excluded(df):
        drop_idx = df[df.fname.isin(exclude_files)].index.tolist()
        # df.ix[drop_idx,:].to_csv(WORKING_DIR + '/file_idx-dropped-excluded.csv')
        df = df.drop(drop_idx,axis=0).reset_index(drop=True)
        return df
    def gen_new_f_from_all_file_json(json_fpath):
        to_sql('drop table if exists new_f;')
        pd.read_json(json_fpath).to_sql('new_f',eng)
        to_sql("""
            with
                sel as (select array_agg(md5) all_md5s from agreements)
                ,to_rm as (select array_agg(n.uid) rm_uids from new_f n, sel s where array[n.md5::uuid] && s.all_md5s)
            delete from new_f n using to_rm t where array[n.uid] && t.rm_uids;
               """)
    def continue_uid_from_agreements():

        df=pd.read_sql('select * from new_f',eng)

        null_uid = df[df.uid.isnull()].index.tolist()
        if null_uid:
            df.drop(null_uid,axis=0,inplace=True)

        df['new_uid'] = None

        max_uid = pd.read_sql("""
            select
                case when f1.m_uid>f2.m_uid then f1.m_uid else f2.m_uid end r
            from
                (select max(uid) m_uid from agreements) f1
                ,(select max(uid) m_uid from agreements_skipped) f2
            """,eng).r.tolist()[0]

        new_uid = max_uid + 1
        for i,r in df.iterrows():
            df.set_value(i,'new_uid',new_uid)
            new_uid += 1
        to_sql('drop table if exists tmp_new_f;')
        if df.columns.tolist().count('last_updated'):
            df.drop('last_updated',axis=1,inplace=True)
        df.to_sql('tmp_new_f',eng)

        if not df.columns.tolist().count('tmp'):
            to_sql("alter table new_f add column tmp integer;")

        to_sql("""
                with sel as (select * from tmp_new_f)
                update new_f n set tmp=s.new_uid
                from sel s
                where s.uid=n.uid;

                drop table if exists tmp_new_f;
                create table tmp_new_f as (select tmp uid,fext,fname,fpath,md5,f_last_modified,f_created from new_f);

                drop table new_f;
                alter table tmp_new_f rename to new_f;
               """)
        return
    def rm_dupe_md5():
        """
        with
            sel as (select array_agg(md5) all_md5s from agreements)
            ,to_rm as (select array_agg(n.uid) rm_uids from new_f n, sel s
                       where array[n.md5::uuid] && s.all_md5s)
        delete from new_f n using to_rm t
        where array[n.uid] && t.rm_uids;
        """
        df = pd.read_sql("select * from new_f",eng)
        df['rm'] = False
        df['rm_note'] = None
        df.fext = df.fext.str.lower()
        all_md5 = df.md5.tolist()
        df['md5_cnt'] = df.md5.map(lambda s: all_md5.count(s))

        # Mark files with same md5 ... setting 'rm' for all but most recent dupe md5
        fix = df[df.md5_cnt!=1].copy()
        fix['f_latest'] = False
        fix = fix.sort_values(['md5','f_last_modified'],ascending=[True,False]).reset_index(drop=True)
        grps = fix.groupby('md5')
        for k,v in grps.groups.iteritems():
            gf = fix.ix[v,:].copy()
            gf = gf.sort_values('f_last_modified',ascending=False).reset_index(drop=True)
            latest_idx = fix[fix.uid==gf.ix[0,'uid']].index.tolist()[0]
            fix.set_value(latest_idx,'f_latest',True)

        drop_uids = fix[fix.f_latest==False].uid.tolist()
        for i,r in fix[fix.uid.isin(drop_uids)].iterrows():
            idx = df[df.uid==r['uid']].index.tolist()[0]
            df.set_value(idx,'rm',True)
            df.set_value(idx,'rm_note','dupe md5 when consolidating; took most recently modified; rm this')

        assert len(df[df.rm==True]) == len(df[df.rm_note.isnull()==False])

        sf = df[df.rm==True].copy()

        if len(sf)>0:
            to_sql('drop table if exists tmp_new_f')
            sf.to_sql('tmp_new_f',eng)
            q = """
                insert into agreements_skipped (uid,fext,fname,fpath_orig,md5,f_last_modified,f_created,notes)
                select
                    t.uid,t.fext,t.fname,t.fpath,t.md5::uuid
                    ,to_timestamp(t.f_last_modified)::timestamp without time zone
                    ,to_timestamp(t.f_created)::timestamp without time zone
                    ,t.rm_note
                from tmp_new_f t where t.rm is true;

                with sel as (select array_agg(uid) all_uids from agreements_skipped)
                delete from new_f n using sel s
                where array[n.uid] && s.all_uids;

                drop table if exists tmp_new_f;

                """
            to_sql(q)
            df = pd.read_sql("select * from new_f",eng)

        return

    def update_agreements_with_new_files(df):
        if df.columns.tolist().count('fpath'):
            df.rename(columns={'fpath':'fpath_orig'},inplace=True)
        df['is_new'] = True
        to_sql('drop table if exists new_f; drop table if exists tmp_new_f;')
        df.to_sql('new_f',eng)
        to_sql("""
            insert into agreements (uid,fext,fname,fpath_orig,fpath_cons,md5,f_last_modified,f_created,is_new)
            select
                t.uid,t.fext,t.fname,t.fpath_orig,t.fpath_cons,t.md5::uuid
                ,to_timestamp(t.f_last_modified)::timestamp without time zone
                ,to_timestamp(t.f_created)::timestamp without time zone
                ,true
            from new_f t;

            drop table if exists new_f;

            """)
        return
    def get_new_fpaths(chk_list=None,dest_dir=None):
        chk_list=[it.hex for it in pd.read_sql('select md5 r from agreements',eng).r.tolist()]
        if not dest_dir:
            dest_dir = '/home/kali/PROJECTS/INTARCIA/AGREEMENTS_cons'
        df = get_file_list(dest_dir)
        df['md5'] = df.fpath.map(lambda s: md5(s) )
        return df[df.md5.isin(chk_list)==False].fpath.tolist()

    def old_method():
        save_changes = []
        fix_list = sorted(fix.fpath_cons.unique().tolist())
        for it in fix_list:
            mod_idx = fix[fix.fpath_cons==it].sort_values('f_last_modified').index.tolist()
            for n in range(len(mod_idx)):
                idx,ver = mod_idx[n],n+1
                pt = df.iloc[idx]
                old_fpath_cons = pt['fpath_cons']
                _pattern = r'(.*)(\.'+pt['fext']+r')$'
                _repl = r'\1_'+str(ver)+r'\2'
                _string = pt['fpath_cons']
                new_fpath_cons = re.sub(_pattern,_repl,_string,count=1)
                save_changes.append({'old_fpath_cons':old_fpath_cons,'new_fpath_cons':new_fpath_cons})
                df.set_value(idx,'fpath_cons',new_fpath_cons)

        pd.DataFrame(save_changes).to_csv(WORKING_DIR + '/file_idx-renamed-fpath_cons.csv')

        # confirm no dupes
        all_fpath_cons = df.fpath_cons.tolist()
        all_md5 = df.md5.tolist()
        df['fpath_cons_cnt'] = df.fpath_cons.map(lambda s: all_fpath_cons.count(s))
        df['md5_cnt'] = df.md5.map(lambda s: all_md5.count(s))
        assert len(df[(df.fpath_cons_cnt!=1)&(df.md5_cnt==1)])==0, 'Issue with de-duping consolidated fpath'

        # remove all but one row in groups with dupe md5 AND dupe fpath_cons
        rm_fpath_cons_md5_list = sorted(df[df.md5_cnt!=1].md5.unique().tolist())

        start_cnt = len(df)
        save_df = df.ix[-1:-1,:]
        for it in rm_fpath_cons_md5_list:
            drop_idx = df[df.md5==it].index.tolist()[1:]
            save_df = save_df.append(df.ix[drop_idx,:])
            df.drop(drop_idx,axis=0,inplace=True)
        assert start_cnt==(len(save_df)+len(df)),'Issue with count of dropped-dupes-matching-fpath_cons-and-md5'
        save_df.to_csv(WORKING_DIR + '/file_idx-dropped-dupes-matching-fpath_cons-and-md5.csv')
        assert len(df.fpath_cons.unique())==len(df.md5.unique())==len(df),'Issue with unique md5 count during processing'

        # final confirmation that result have no dupes
        all_fpath_cons = df.fpath_cons.tolist()
        df['fpath_cons_cnt'] = df.fpath_cons.map(lambda s: all_fpath_cons.count(s))
        assert len(df[df.fpath_cons_cnt!=1])==0

    # clean_workspace()

    raise SystemError

    update_json_fpath = '2016.10.28_file_index_AGREEMENTS.json'

    gen_new_f_from_all_file_json(update_json_fpath)
    continue_uid_from_agreements()
    rm_dupe_md5()
    assert pd.read_sql("""
            with sel as (select array_agg( fname ) all_fname from agreements where is_new is false)
            select count(n.*) cnt from
            new_f n, sel s
            where array[n.fname] && s.all_fname
            """,eng).cnt[0]==0,'unhandled instance:  possible that new file now presents an fname dupe of existing, which result in overwriting or duplicative files'
    df = get_consolidated_paths_and_enum_dupes()
    df = remove_excluded(df)
    update_agreements_with_new_files(df)
    q1=pd.read_sql("select count(distinct uid) cnt from agreements",eng).cnt[0]
    q2=pd.read_sql("select count(distinct fpath_cons) cnt from agreements",eng).cnt[0]
    assert q1==q2,'possible file overwrite when copying file to "%s"' % consol_dir

    df.to_json('%s_to_cons.json' % update_json_fpath[:-5])


    def check_and_copy_fpaths():
        base_dir = '/home/kali/PROJECTS/INTARCIA'

        dest_dir = '%s/AGREEMENTS_cons' % base_dir
        src_dir = '%s/scripts/new_files/AGREEMENTS_cons' % base_dir

        dest_dir_files = os.listdir(dest_dir)

        # Remove all matching md5 regardless of fname
        df['chk_md5'] = df[df.fpath_cons.isin(dest_dir_files)].fpath_cons.map(lambda s: md5(s) )
        drop_idx = df[df['chk_md5']==df['md5']].index.tolist()
        df.ix[drop_idx,'fpath_cons'].map(lambda s: os.remove(s))

        df.drop(drop_idx,axis=0,inplace=True)

        # Find matching fnames, flagging if different md5s else removing src copy
        drop_idx = []
        for i,r in df[df.fname.isin(dest_dir_files)].iterrows():
            chk_md5 = md5(r['fpath_cons'])
            if r['md5']!=chk_md5:
                print 'same name/diff md5:',r['fname']
                raise SystemError
            else:
                os.remove(r['fpath_cons'])
                drop_idx.append(i)
        df.drop(drop_idx,axis=0,inplace=True)




    """
    FROM_DIR="/home/kali/PROJECTS/INTARCIA/scripts/new_files/AGREEMENTS_cons"
    TO_DIR="/home/kali/PROJECTS/INTARCIA/AGREEMENTS_cons"
    for i in $(env ls -1 $FROM_DIR); do
        if [[ -n "$(env ls -1 $TO_DIR|grep $i)" ]]; then
            if [[ "$(md5sum $FROM_DIR/$i|cut -d ' ' -f1)" != "$(md5sum $TO_DIR/$i|cut -d ' ' -f1)" ]]; then
                echo "copy $FROM_DIR/$i to $TO_DIR/$i"  >> _out
                # cp "$FROM_DIR/$i" "$TO_DIR/"
            else
                echo "rm $FROM_DIR/$i" >> _out
            fi
        fi
    done

    """

    # copy files into single directory and rename with fpath_cons values
    df['fpath_escaped'] = df.fpath_.map(lambda s: s.replace('$',r'\\\$'))
    cmds = df.ix[:,['fpath_escaped','fpath_cons']].apply(lambda s: """cp \\"%s\\" %s""" % tuple(s),axis=1).tolist()
    for c in cmds:
        r = run_cmd('/bin/bash -c "' + c + '" 2>&1;')
        assert r=='', 'Error with cmd: "'+c+'", res: '+r

    drop_cols = ['fpath_cons_cnt','fpath_escaped','md5_cnt']
    df.drop(drop_cols,axis=1,inplace=True)

    return df

def integrate_native_file_attr_vals(df):
    run_cmd("lynx --dump -nomargins -dont_wrap_pre <(cat file_info) > file_info2; mv file_info2 file_info")
    with open(WORKING_DIR + '/file_info') as f: file_attrs=f.read().split('\n')

    prefix_len=len('L:\\AGREEMENTS\\')
    suffix_len=len(' 08/04/2014 15:38:10 08/04/2014 15:38:10')
    change_list=[]
    for f in file_attrs:
        z=f[prefix_len:-suffix_len]
        z_name=z[z.rfind('\\')+1:]
        idx = df[df.fname==z_name].first_valid_index()
        if idx:
            change_list.append(z_name)

            z_f_info=f[-suffix_len:].strip()
            mid_pt = len(z_f_info)/2
            z_creation = z_f_info[:mid_pt].strip()
            z_creation = DT.datetime.strptime(z_creation,'%d/%m/%Y %H:%M:%S')
            z_modification=z_f_info[:mid_pt].strip()
            z_modification = DT.datetime.strptime(z_modification,'%d/%m/%Y %H:%M:%S')

            df.set_value(idx,'f_created',calendar.timegm(z_creation.timetuple()))
            df.set_value(idx,'f_last_modified',calendar.timegm(z_modification.timetuple()))

    return df

def load_initial_file_index():
    nf=pd.read_csv(WORKING_DIR + '/file_idx_initial.csv')
    nf.drop(['Unnamed: 0'],axis=1,inplace=True)
    nf.f_last_modified=nf.f_last_modified.astype(int)
    nf.f_created=nf.f_created.astype(int)
    return nf

def make_initial_file_index():
    global DOC_SRC_DIR
    abs_path = run_cmd("stat -c '%N' "+DOC_SRC_DIR).strip("'")
    df = get_file_list(abs_path)
    assert type(df)!=bool and len(df)>0,'Issue with getting file paths from dir: '+abs_path
    df.fpath = df.fpath.str.replace('/home/ubx','~')
    df['md5'] = df.fpath.map(lambda s: md5(s))
    df['f_last_modified'] = df.fpath.map(lambda s: file_attribute(s,'file_mod_epoch'))
    df.f_last_modified=df.f_last_modified.astype(int)
    df['f_created'] = df.fpath.map(lambda s: file_attribute(s,'file_birth_epoch'))
    df.f_created=df.f_created.astype(int)
    df = integrate_native_file_attr_vals(df)
    df.to_csv(WORKING_DIR + '/file_idx_initial.csv')
    return df


class SQL:

    def __init__(self,parent=None):
        pass

    class CREATE:

        def __init__(self,parent=None):
            pass

        def z_extract():
            q="""
                drop function if exists z_extract_pdf( fpath text ) cascade;
                create function z_extract_pdf( text,boolean with default false )
                RETURNS TEXT as E'
                #!/bin/bash
                #/usr/bin/lynx --dump -nomargins -dont_wrap_pre <(/usr/bin/pdftotext -q -nopgbrk "$1" - | /usr/bin/enca -L __ -P -x UTF8)
                res=$(/usr/bin/pdftotext -q -nopgbrk "$1" - | /usr/bin/enca -L __ -P -x UTF8 | /usr/bin/lynx --stdin --dump -nomargins -dont_wrap_pre)
                [[ -z $res ]] && \\
                    echo "$res" || \\
                /usr/bin/pdftotext -q -nopgbrk "$1" - | /usr/bin/enca -L __ -P -x UTF8
                ' LANGUAGE PLSHU;
                """
            to_sql(q)
# to_sql(q.replace('    ',''))


if __name__ == '__main__':
    from sys import argv
    args = argv[1:]
    print args
    FROM_CMD_LINE=True

    if not args:
        raise SystemExit
    else:
        import sys
        if len(args)>1:
            if type(args[-1])==dict:
                getattr(sys.modules[__name__],args[0])(args[1:-1],args[-1])
            else:
                getattr(sys.modules[__name__],args[0])(*args[1:])
        else:
            getattr(sys.modules[__name__],args[0])()
