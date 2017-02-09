# -*- encoding: utf-8 -*-
from lazyblacksmith.models import TaskState


def is_task_running(id, scope):
    """ Returns if a task is already running/queued """
    task = TaskState.query.filter(
        TaskState.id == id,
        TaskState.scope == scope,
        TaskState.state.in_([TaskState.QUEUED, TaskState.RUNNING])
    ).one_or_none()
    return task is not None