# coding=utf-8
import re
from eventlet_httpd.core.view import View
from eventlet_httpd.http.error import Http404, Http500


class Route(object):
    def __init__(self, url, method, func, name=None, *args, **kwargs):
        super(Route, self).__init__()
        self.name = name
        self.method = method
        self.defaults = kwargs.get('defaults', {})
        self.url_params = {}
        self._set_func(func)
        self._compile_url(url)

    def _set_func(self, func):
        if not (callable(func) or issubclass(func, View)):
            raise Http500('%s is not callable, or is not subclass of View')
        self.func = func

    def _compile_url(self, url):
        self.url = url
        if self.url == '':
            self.url = '/'

        matches = re.findall('<(.+?)>', self.url)
        self.compiled_url = self.url

        if matches:
            for m in matches:
                tmp = m.partition(':')
                key = tmp[0]
                reg_str = tmp[2]

                if reg_str == '':
                    reg_str = '.+?'

                fake_reg_str = '<%s>' % m
                real_reg_str = '(?P<%s>%s)' % (key, reg_str)
                self.compiled_url = self.compiled_url.replace(fake_reg_str, real_reg_str)

        self.compiled_url = '^%s$' % self.compiled_url

    def match(self, request):
        self.url_params = {}

        if self.method == '*' or self.method == request.method:
            matches = re.match(self.compiled_url, request.url)

            if matches:
                self.url_params = matches.groupdict()
                return True

        return False

    def execute(self, request):
        params = {}
        params.update(self.defaults)
        params.update(self.url_params)

        if issubclass(self.func, View):
            view = self.func()
            method = request.method.lower()
            if not hasattr(view, method):
                raise Http404()
            func = getattr(view, method)

        elif callable(self.func):
            func = self.func(request, **params)

        else:
            raise Http404()

        return func(request, **params)