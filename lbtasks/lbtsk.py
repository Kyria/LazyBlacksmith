# -*- encoding: utf-8 -*-
from functools import wraps

import config

from .huey_app import create_app

APP, HUEY = create_app(config)

def lbtsk(as_argument=False, **kwargs):
    """Force flask context into huey tasks. Because we need it?

    Using decorator, it would give something like the following:
    @huey.task(...)
    @push_flask_context(...)
    def our_function():
        pass

    So we are doing two decorator inside this one, and do all at once
    hiding completely @huey.task, also allowing us to configure whatever
    we want for all tasks at once (and it's shorter to write!...)
    """
    def flask_context(func):
        @wraps(func)
        def inner(*args, **kwargs):
            with APP.app_context():
                if as_argument:
                    return func(APP, *args, **kwargs)
                else:
                    return func(*args, **kwargs)
        return inner

    def actual_task_decorator(func):
        return HUEY.task(**kwargs)(flask_context(func))
    return actual_task_decorator

# kwargs task() <-- param for taskwrapper == task_base base Task class