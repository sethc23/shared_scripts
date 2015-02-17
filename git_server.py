from os import path as os_path
from os import getcwd as os_getcwd
from git import Repo,Actor

# Get Current Sub Repo
here = os_getcwd()
here = here.rstrip('/.git')
system_config = '/home/jail/home/serv/system_config'

# STEP 1:
# Open Current Repo
r=Repo(here)
BASE_DIR = here.replace(system_config+'/','')

# Get Branches, Make Dictionary Index
B=[it.name for it in r.heads]
b=dict(zip(B,range(len(B))))

# Update 'tmp' branch from 'master'
## -    Move HEAD to 'master'
r.head.reference = r.heads[b['master']]
## -    Get all new commits
NEW     =   list(r.iter_commits('%s..%s' % (r.heads['tmp'].commit.hexsha,r.heads['master'].commit.hexsha)))
# -     Reverse Commit List so as to replay commits on Master Repo
NEW.reverse()
# -     Get Changes for Each New Commit Since Previous Commit
##      -   Get Ref Since Last Commit to Master Repo (starting point)
##      -   Save Diff between Starting Point and Next Update
##      -   Move Head up to Next Update until no more Updates
updates =   []
CURR    =   r.heads['tmp'].commit.hexsha
r.head.reference = r.heads[b['tmp']]
for it in NEW:
    r.head.reset(commit=CURR,index=True, working_tree=True)
    c=r.index.diff(it.hexsha)[0]
    c_info = {'author':it.committer.name,'msg':it.message}
    if c.new_file:
        d={'action':'new_file','new_path':os_path.join(BASE_DIR,c.b_blob.path)}
        d.update(c_info)
        updates.append(d)
    if c.deleted_file:
        d={'action':'deleted_file','old_path':os_path.join(BASE_DIR,c.a_blob.path)}
        d.update(c_info)
        updates.append(d)
    if c.renamed:
        d={'action':'renamed',
           'old_path':os_path.join(BASE_DIR,c.a_blob.path),
           'new_path':os_path.join(BASE_DIR,c.b_blob.path)}
        d.update(c_info)
        updates.append(d)
    if [c.new_file,c.deleted_file,c.renamed].count(True)==0:
        d={'action':'updated_file','path':os_path.join(BASE_DIR,c.b_blob.path)}
        d.update(c_info)
        updates.append(d)
    CURR = it.hexsha

## -	Move HEAD to 'tmp'
r.head.reference = r.heads[b['tmp']]
## -	Reset HEAD from 'master' contents
r.head.reset(commit=r.heads['master'].commit.hexsha,index=True, working_tree=True)

# Change repo to system_config
r       =   Repo(system_config)
I       =   r.index

# Replay Updates
for it in updates:
    if it['action']=='new_file':
        I.add([os_path.join(r.working_tree_dir, it['new_path'])])

    elif it['action']=='updated_file':
        I.add([os_path.join(r.working_tree_dir, it['path'])])

    elif it['action']=='deleted_file':
        for (path, stage), entry in I.entries.items():
            if path.find(it['old_path'])>=0 and stage==0:
                I.remove([path])

    elif it['action']=='renamed':
        for (path, stage), entry in I.entries.items():
            if path.find(it['old_path'])>=0 and stage==0:
                I.remove([path])
                I.add([os_path.join(r.working_tree_dir, it['new_path'])])

    author = Actor(it['author'],'blinddiver@gmail.com')
    committer = Actor('serv','blinddiver@gmail.com')
    I.commit(it['msg'],author=author, committer=committer)

g=r.remotes[0]
g.push()