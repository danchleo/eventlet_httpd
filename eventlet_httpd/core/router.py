# coding=utf-8
from eventlet_httpd.core.route import Route


class Router(object):
    def __init__(self):
        self.routes = {}
        super(Router, self).__init__()

    def add(self, url, method, func, *args, **kwargs):
        name = kwargs.pop('name', url)
        self.routes[name] = Route(url, method, func, *args, **kwargs)

    def search(self, request):
        for name in self.routes:
            if self.routes[name].match(request):
                return self.routes[name]

        return None