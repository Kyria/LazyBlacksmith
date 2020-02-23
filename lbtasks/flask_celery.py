# -*- encoding: utf-8 -*-
""" FlaskCelery class """
from __future__ import absolute_import

from celery import Celery
import flask


class FlaskCelery(Celery):
    """ Redefine the Celery object init. """

    def __init__(self, *args, **kwargs):
        super(FlaskCelery, self).__init__(*args, **kwargs)
        if 'app' in kwargs:
            self.init_app(kwargs['app'])

    def init_app(self, app):
        """ init celery app with flask app """
        self.app = app
        self.config_from_object(app.config, namespace='CELERY')


celery_app = FlaskCelery(
    'lbtasks',
    task_cls='lbtasks.lbtsk:LbTsk'
)
