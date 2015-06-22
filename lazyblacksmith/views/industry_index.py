# -*- encoding: utf-8 -*-
from flask import abort
from flask import Blueprint
from flask import render_template

industry = Blueprint('industry', __name__)

@industry.route('/')
def industry_index():
    return ""