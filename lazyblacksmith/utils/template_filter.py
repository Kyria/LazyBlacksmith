# -*- encoding: utf-8 -*-
import humanize

import flask
import jinja2

templatefilter = flask.Blueprint('filters', __name__)


@jinja2.contextfilter
@templatefilter.app_template_filter()
def intcomma(context, value):
    return humanize.intcomma(value)


@jinja2.contextfilter
@templatefilter.app_template_filter()
def intword(context, value):
    return humanize.intword()


@jinja2.contextfilter
@templatefilter.app_template_filter()
def naturalday(context, value, format='%b %d'):
    return humanize.naturalday(value, format)


@jinja2.contextfilter
@templatefilter.app_template_filter()
def naturaltime(context, value, future=False, months=True):
    return humanize.naturaltime(value, future, months)


@jinja2.contextfilter
@templatefilter.app_template_filter()
def duration(context, seconds):
    """Turn a duration in seconds into a human readable string"""
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    parts = []
    if d:
        parts.append('%dd' % (d))
    if h:
        parts.append('%dh' % (h))
    if m:
        parts.append('%dm' % (m))
    if s:
        parts.append('%ds' % (s))
    return ' '.join(parts)
