# -*- encoding: utf-8 -*-
from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import url_for

from lazyblacksmith.extension.cache import CACHE

home = Blueprint('home', __name__)


@home.route("/")
def index():
    return redirect(url_for("blueprint.search"))


@home.route('/legal')
@CACHE.cached(timeout=3600 * 24 * 7)
def legal():
    return render_template('legal.html')
