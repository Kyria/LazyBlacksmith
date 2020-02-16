# -*- encoding: utf-8 -*-
import celery
import flask

from sqlalchemy.exc import SQLAlchemyError
from lazyblacksmith.extension.esipy import esisecurity
from lazyblacksmith.models import TokenScope
from lazyblacksmith.models import db


class LbTsk(celery.Task):
    """ Base class for task, that defines some basic methods, such as
    update for the task state, and allow to get the token_scope easily """

    def __call__(self, *args, **kwargs):
        if flask.has_app_context():
            return super(LbTsk, self).__call__(self, *args, **kwargs)
        with self.app.app_context():
            return super(LbTsk, self).__call__(self, *args, **kwargs)

    def run(self, *args, **kwargs):
        """We don't implement it here. So let's take exactly
        the same as default... for linting..."""
        raise NotImplementedError('Tasks must define the run method.')

    def get_token_update_esipy(self, character_id, scope):
        """ get token, update it and return everything
        Get the token using what have been given in parameter
        then try to update esisecurity, verify the token is
        up to date and catch any APIException while updating
        it to be able to invalidate wrong tokens.
        """
        token = TokenScope.query.filter(
            TokenScope.user_id == character_id,
            TokenScope.scope == scope
        ).one()
        esisecurity.update_token(token.get_sso_data())

        if esisecurity.is_token_expired():
            token.update_token(esisecurity.refresh())
            try:
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()

        return token

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """ if failure, force db rollback before anything else """
        db.session.rollback()

    def on_success(self, retval, task_id, args, kwargs):
        """ force commit if success """
        db.session.commit()
