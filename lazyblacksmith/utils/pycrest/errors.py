class APIException(Exception):
    def __init__(self, url, code, json_response):

        self.url = url
        self.status_code = code
        self.response = json_response

    def __str__(self):
        if 'error' in self.response:
            return 'HTTP Error %s: %s' % (self.status_code,
                                          self.response['error'])
        elif 'message' in self.response:
            return 'HTTP Error %s: %s' % (self.status_code,
                                          self.response['message'])
        else:
            return 'HTTP Error %s' % (self.status_code)


class UnsupportedHTTPMethodException(Exception):
    def __init__(self, method):
        self.method = method

    def __str__(self):
        return 'Unsupported HTTP Method: %s' % (self.method)
