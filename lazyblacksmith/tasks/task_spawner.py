# -*- encoding: utf-8 -*-
from .character.character_skills import update_character_skills_task
from lazyblacksmith.utils.time import utcnow
from lazyblacksmith.models import db
from lazyblacksmith.models import User
from lazyblacksmith.models import TokenScope
from lazyblacksmith.models import TaskState
from lazyblacksmith.extension.celery_app import celery_app


TASK_SCOPE = {
    TokenScope.SCOPE_SKILL: update_character_skills_task,
    TokenScope.SCOPE_CLONES: None,
    TokenScope.SCOPE_CHAR_ASSETS: None,
    TokenScope.SCOPE_CORP_ASSETS: None,
}

@celery_app.task(name="task_spawner")
def spawn_tasks():
    """ Task triggered every minutes that scan all tasks done to find 
    any task to do (based on the cached_until field) """
    now = utcnow()

    all_tokens = TokenScope.query.all()
    for token_scope in all_tokens:
        print "char: %s - token: %s" % (token_scope.user_id, token_scope.scope)
        # if no task is defined for the scope, skip it
        if (token_scope.scope not in TASK_SCOPE or
           TASK_SCOPE[token_scope.scope] is None):
            continue

        # check if there is no running task, and the data is not still cached
        if ((not token_scope.cached_until or token_scope.cached_until <= now) 
           and not is_task_running(token_scope.user_id, token_scope.scope)):
            print "lets start"
            task = TASK_SCOPE[token_scope.scope]
            task_id = "%s-%s-%s" % (
                now.strftime('%Y%m%d-%H%M%S'),
                task.__name__,
                token_scope.user_id
            )
            token_state = TaskState(
                task_id=task_id,
                id=token_scope.user_id,
                scope=token_scope.scope,
            )
            db.session.add(token_state)
            db.session.commit()

            task.s(token_scope.user_id).apply_async(task_id=task_id)
        
def is_task_running(id, scope):
    task = TaskState.query.filter(
        TaskState.id == id,
        TaskState.scope == scope,
        TaskState.state.in_([TaskState.QUEUED, TaskState.RUNNING])
    ).one_or_none()
    print "is running : %s" % (task is not None)
    return task is not None