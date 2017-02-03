# -*- encoding: utf-8 -*-
from lazyblacksmith.extension.celery_app import celery_app
from lazyblacksmith.models import db
from lazyblacksmith.models import TaskState
from lazyblacksmith.models import TokenScope
from lazyblacksmith.utils.time import utcnow

class LbTask(celery_app.Task):
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
        
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        self.end(TaskState.FAILURE)