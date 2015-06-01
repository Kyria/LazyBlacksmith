# -*- encoding: utf-8 -*-
import jinja2
import flask

evefilter = flask.Blueprint('evefilters', __name__)

@jinja2.contextfilter
@evefilter.app_template_filter()
def market_link(context, value):
    return value
