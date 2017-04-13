# -*- encoding: utf-8 -*-
from lazyblacksmith.extension.celery_app import celery_app
from lazyblacksmith.models import TaskState
from lazyblacksmith.models import TokenScope
from lazyblacksmith.models import db
from lazyblacksmith.utils.time import utcnow


class LbTask(celery_app.Task):
    """ Base class for task, that defines some basic methods, such as
    update for the task state, and allow to get the token_scope easily """
    def start(self):
        task_state = TaskState.query.get(self.request.id)
        if task_state:
            task_state.start_date = utcnow()
            task_state.state = TaskState.RUNNING
            try:
                db.session.commit()
            except:
                db.session.rollback()

    def end(self, state):
        task_state = TaskState.query.get(self.request.id)
        if task_state:
            task_state.end_date = utcnow()
            if state in TaskState.STATES:
                task_state.state = state
            else:
                task_state.state = TaskState.UNKNOWN

            try:
                db.session.commit()
            except:
                db.session.rollback()

    def get_token_scope(self, user_id, scope):
        return TokenScope.query.filter(
            TokenScope.user_id == user_id,
            TokenScope.scope == scope
        ).one()

    def inc_fail_token_scope(self, token, status_code):
        """ Check if status_code is 4xx, increase counter, check validity """
        if int(status_code / 100) == 4:
            token.request_try += 1
            token.valid = True if token.request_try <= 3 else False
            try:
                db.session.commit()
            except:
                db.session.rollback()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # if failure, force db rollback before anything else, just in case
        db.session.rollback()
        self.end(TaskState.FAILURE)
