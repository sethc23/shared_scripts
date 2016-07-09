from os                                     import environ                  as os_environ
from sys                                    import path                     as py_path
py_path.append(                                 os_environ['HOME'] + '/.scripts')
from system_settings                        import *
from celery                                 import Celery
from re                                     import match                    as re_match

# http://docs.celeryproject.org/en/latest/userguide/routing.html
class Router(object):

    def route_for_task(self, task, args=None, kwargs=None):
        parts = task.split('.')
        if re_match(r'^mp[a-z_]+\.sync\.[a-z_]+$', task) is not None:
            return {
                'routing_key': task,
                'queue': parts[0] + '.sync',
                }
        elif re_match(r'^mp[a-z_]+\.async\.[a-z_]+$', task) is not None:
            return {
                'routing_key': task,
                'queue': parts[0] + '.async',
                }
        return None

def _get_celery_queues():
    services = [
        'sys_serv_tasks',
        ]

    queues = {}
    for service in services:
        queues[service] = {
            'binding_key': service,# + '.#',
            'exchange': service,
            'exchange_type': 'direct',
            'delivery_mode': 2,
            }
        # queues[service + '.async'] = {
        #     'binding_key': service + '.async.#',
        #     'exchange': service,
        #     'exchange_type': 'direct'
        #     }
    return queues

class CeleryConfig(object):

    # Routing:
    CELERY_ROUTES                   =   (Router(),)

    #: Only add pickle to this list if your broker is secured
    #: from unwanted access (see userguide/security.html)
    #CELERY_ACCEPT_CONTENT           =   ['pickle']
    CELERY_ACCEPT_CONTENT           =   ['json','pickle']
    CELERY_TASK_SERIALIZER          =   'json'      #'pickle'
    CELERY_RESULT_SERIALIZER        =   'json'      #'pickle'
    #CELERY_TASK_SERIALIZER          =   'pickle'
    #CELERY_RESULT_SERIALIZER        =   'pickle'
    CELERY_TIMEZONE                 =   'US/Eastern'
    CELERY_ENABLE_UTC               =   False

    # CELERY_RESULT_BACKEND           =   'redis://localhost/0'
    # .. which by default, port=6379, db=0
    # CELERY_IGNORE_RESULT            =   False
    REDIS_CONNECT_RETRY             =   True
    # REDIS_HOST                      =   "localhost"
    # REDIS_PORT                      =   6379
    # REDIS_DB                        =   "0"
    CELERY_SEND_EVENTS              =   True
    # CELERY_RESULT_BACKEND           =   "redis"
    # CELERY_RESULT_PORT              =   6379


    # Replicate queues to all nodes in the cluster
    CELERY_QUEUE_HA_POLICY          =   'all'

    # http://docs.celeryproject.org/en/latest/userguide/tasks.html#disable-rate-limits-if-they-re-not-used
    CELERY_DISABLE_RATE_LIMITS      =   True

    CELERY_QUEUES                   =   _get_celery_queues()
    BROKER_HEARTBEAT                =   10
    BROKER_HEARTBEAT_CHECKRATE      =   2.0
    BROKER_POOL_LIMIT               =   0

    # Logging:
    #CELERYD_HIJACK_ROOT_LOGGER      =   False
                                    # above default: true
    #CELERY_REDIRECT_STDOUTS         =   False
                                    # above default: true
    #CELERY_REDIRECT_STDOUTS_LEVEL   =   'INFO'
                            # DEBUG, INFO, WARNING (default), ERROR or CRITICAL

    # # Enables error emails.
    # CELERY_SEND_TASK_ERROR_EMAILS = True

    # # Name and email addresses of recipients
    # ADMINS = (
    #     ('George Costanza', 'george@vandelay.com'),
    #     ('Cosmo Kramer', 'kosmo@vandelay.com'),
    # )

    # # Email address used as sender (From field).
    # SERVER_EMAIL = 'no-reply@vandelay.com'

    # # Mailserver configuration
    # EMAIL_HOST = 'mail.vandelay.com'
    # EMAIL_PORT = 25
    # # EMAIL_HOST_USER = 'servers'
    # # EMAIL_HOST_PASSWORD = 's3cr3t'

def celery_apps_factory(app_type, sync_broker_url, async_broker_url, backend, service_name):
    backend                                 =   'redis://localhost:6380' if backend=='redis' else 'amqp'
    protocol                                =   'amqp' if app_type == 'SUBSCRIBER' else 'librabbitmq'

    if sync_broker_url==None:   sync_app    =   ''
    else:
        broker_url_sync                     =   protocol + '://' + sync_broker_url
        sync_app                            =   Celery(service_name, backend=backend, broker=broker_url_sync)
        sync_app.config_from_object(            CeleryConfig)

    if async_broker_url==None:  async_app   =   ''
    else:
        broker_url_async                    =   protocol + '://' + async_broker_url
        async_app                           =   Celery(service_name + '.async_app', broker=broker_url_async)
        async_app.config_from_object(           CeleryConfig)
        async_app.conf.CELERY_IGNORE_RESULT =   True

    return sync_app, async_app

# Router-to-celery_apps_factory taken from http://www.tuicool.com/articles/Fna2em


BROKER_URL              = THIS_PC + ':mq_money@localhost//'

# # Example App Initialization:
# sync_app, async_app     = celery_apps_factory(
#     app_type            = 'SUBSCRIBER',
#     # app_type            = 'PUBLISHER',
#     sync_broker_url     = BROKER_URL,
#     async_broker_url    = None,
#     backend             = 'amqp',
#     service_name        = 'document_processing',
#     )

