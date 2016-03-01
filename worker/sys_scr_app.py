

from app_factory                            import *

sync_app, async_app                         =   celery_apps_factory(
                                                app_type                    =   'SUBSCRIBER',
                                                sync_broker_url             =   BROKER_URL,
                                                async_broker_url            =   None,
                                                backend                     =   'redis',
                                                service_name                =   'sys_scr_app',
                                                )

from sys_scr_tasks                          import *