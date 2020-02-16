# -*- encoding: utf-8 -*-
""" FlaskCelery class """
from __future__ import absolute_import

from celery import Celery


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


CELERY_APP = FlaskCelery(
    task_cls='lbtasks.lbtsk:LbTsk'
)
