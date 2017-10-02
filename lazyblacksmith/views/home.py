# -*- encoding: utf-8 -*-
from flask import Blueprint
from flask import render_template

from lazyblacksmith.extension.cache import cache

home = Blueprint('home', __name__)


@home.route("/")
@cache.cached(timeout=3600 * 24)
def index():
    return render_template('base.html')


@home.route('/legal')
@cache.cached(timeout=3600 * 24 * 7)
def legal():
    return render_template('legal.html')
