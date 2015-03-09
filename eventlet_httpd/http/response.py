# coding=utf-8
from eventlet_httpd.core.header import HTTPHeader
from eventlet_httpd.http import HTTPRequest


class HTTPResponse(object):
    def __init__(self, content='', code=200, *args, **kwargs):
        super(HTTPResponse, self).__init__(*args, **kwargs)
        self._headers = HTTPHeader()
        self._headers['Content-Type'] = 'text/plain'

        self._code = code
        self._http_codes = {
            200: '200 OK'
        }
        self._content = content
        self._after_response_hooks = []

    def _get_http_code_info(self):
        if self._http_codes.has_key(self._code):
            return self._http_codes[self._code]

        return self._http_codes[200]

    def add_header(self, key, value):
        self._headers[key] = value

    def clear_header(self, key, value):
        if self._headers.get(key):
            del self._headers[key]

    def raw_headers(self):
        return self._headers.raw_headers()

    def _get_response_content(self):
        if hasattr(self._content, '__iter__'):
            content = self._content

        else:
            content = [str(self._content)]

        return content

    def response(self, start_response, environ):
        environ['eventlet.posthooks'] = []
        if self.has_after_response_hooks():
            environ['eventlet.posthooks'] = [(self.exec_after_response_hooks, (), {})]

        start_response(self._get_http_code_info(), self._headers.raw_headers())

        return self._get_response_content()

    def exec_after_response_hooks(self, environ):
        hooks = self.get_after_response_hooks()

        for hook_data in hooks:
            func = hook_data['func']
            args = hook_data['args']
            kwargs = hook_data['kwargs']

            request = HTTPRequest(environ=environ)
            func(request, *args, **kwargs)

    def register_after_response_hook(self, func, *args, **kwargs):
        self._after_response_hooks.append({'func': func, 'args': args, 'kwargs': kwargs})

    def clear_after_response_hooks(self):
        self._after_response_hooks = []

    def has_after_response_hooks(self):
        return len(self._after_response_hooks)

    def get_after_response_hooks(self):
        return self._after_response_hooks


class HttpResponse404(HTTPResponse):
    def __init__(self, *args, **kwargs):
        super(HttpResponse404, self).__init__(*args, **kwargs)
        self._code = 404
        self._content = '404 Not Found'
        self._http_codes[404] = self._content


class HttpResponse400(HTTPResponse):
    def __init__(self, *args, **kwargs):
        super(HttpResponse400, self).__init__(*args, **kwargs)
        self._code = 400
        self._content = '400 Bad Request'
        self._http_codes[400] = self._content


class HttpResponse403(HTTPResponse):
    def __init__(self, *args, **kwargs):
        super(HttpResponse403, self).__init__(*args, **kwargs)
        self._code = 403
        self._content = '403 Forbidden'
        self._http_codes[403] = self._content


class HttpResponse500(HTTPResponse):
    def __init__(self, *args, **kwargs):
        super(HttpResponse500, self).__init__(*args, **kwargs)
        self._code = 500
        self._content = '500 Internal server error'
        self._http_codes[500] = self._content


class HttpResponse304(HTTPResponse):
    def __init__(self, *args, **kwargs):
        super(HttpResponse304, self).__init__(*args, **kwargs)
        self._code = 304
        self._content = '304 Not Modified'
        self._http_codes[304] = self._content