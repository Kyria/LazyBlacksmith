# -*- encoding: utf-8 -*-
""" Helper to replace removed/deprecated Werkzeug properties """

def is_xhr(request):
    return request.environ.get('HTTP_X_REQUESTED_WITH', '').lower() \
        == 'xmlhttprequest'
