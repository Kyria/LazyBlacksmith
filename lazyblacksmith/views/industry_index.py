# -*- encoding: utf-8 -*-
from flask import Blueprint

industry = Blueprint('industry', __name__)


@industry.route('/')
def industry_index():
    return ""
