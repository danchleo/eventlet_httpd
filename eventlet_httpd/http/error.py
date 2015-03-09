# coding=utf-8
from eventlet_httpd.http.response import HttpResponse304
from eventlet_httpd.http.response import HttpResponse404, HttpResponse400
from eventlet_httpd.http.response import HttpResponse403, HttpResponse500


class HttpError(Exception):
    def __init__(self, *args, **kwargs):
        self.response = None
        super(HttpError, self).__init__(*args, **kwargs)


class Http304(HttpError):
    def __init__(self, *args, **kwargs):
        super(Http304, self).__init__(*args, **kwargs)
        self.response = HttpResponse304()


class Http400(HttpError):
    def __init__(self, *args, **kwargs):
        super(Http400, self).__init__(*args, **kwargs)
        self.response = HttpResponse400()


class Http404(HttpError):
    def __init__(self, *args, **kwargs):
        super(Http404, self).__init__(*args, **kwargs)
        self.response = HttpResponse404()


class Http403(HttpError):
    def __init__(self, *args, **kwargs):
        super(Http403, self).__init__(*args, **kwargs)
        self.response = HttpResponse403()


class Http500(HttpError):
    def __init__(self, *args, **kwargs):
        super(Http500, self).__init__(*args, **kwargs)
        self.response = HttpResponse500()