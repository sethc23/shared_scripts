

osx             =   {   'nginx'             :   'nginx: master process',
                        'syslog-ng'         :   'supervising syslog-ng',
                        'postgres'          :   '/opt/local/lib/postgresql93/bin/postgres -i -D /opt/local/var/db/postgresql93/defaultdb',
                        'supervisor_root'   :   'sudo /opt/local/Library/Frameworks/Python.framework/Versions/Current/bin/supervisord',
                        'uwsgi_aprinto'     :   '/Users/admin/SERVER3/aprinto/ENV/bin/uwsgi --ini',
                        'celery_aprinto'    :   '/Users/admin/SERVER3/aprinto/ENV/bin/celery',
                        'redis'             :   '/opt/local/bin/redis-server',
                        'postfix'           :   '/opt/local/libexec/postfix/master',
                        'sshd'              :   '/opt/local/sbin/sshd',
                        'growl'             :   '/Applications/Growl.app/Contents/MacOS/Growl',
                        'nosleep'           :   '/Applications/Utilities/NoSleep.app/Contents/MacOS/NoSleep'}

osx_mounts      =   {   'ub1'               :   '/opt/local/bin/sshfs ub1:/ /Volumes/ub1',
                        'ub2'               :   '/opt/local/bin/sshfs ub2:/ /Volumes/ub2',
                        'ms1'               :   ''
                    }

print [it+'\n' for it in osx.keys()]