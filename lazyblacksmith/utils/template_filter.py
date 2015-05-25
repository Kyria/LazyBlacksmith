# -*- encoding: utf-8 -*-
import humanize

import jinja2
import flask

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