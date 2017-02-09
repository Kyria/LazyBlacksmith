# -*- encoding: utf-8 -*-
# thanks, i need this for celery... really...
from __future__ import absolute_import

import flask

from celery import Celery


class FlaskCelery(Celery):
    """ Redefine the Celery object init. Also add a patch to add the 
    flask context within tasks """
    
    def __init__(self, *args, **kwargs):

        super(FlaskCelery, self).__init__(*args, **kwargs)
        self.patch_task()

        if 'app' in kwargs:
            self.init_app(kwargs['app'])

    def patch_task(self):
        TaskBase = self.Task
        _celery = self

        class ContextTask(TaskBase):
            abstract = True

            def __call__(self, *args, **kwargs):
                if flask.has_app_context():
                    return TaskBase.__call__(self, *args, **kwargs)
                else:
                    with _celery.app.app_context():
                        return TaskBase.__call__(self, *args, **kwargs)

        self.Task = ContextTask

    def init_app(self, app):
        self.app = app
        self.config_from_object(app.config, namespace='CELERY')

celery_app = FlaskCelery()
