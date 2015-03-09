# coding=utf-8
import types


class HTTPHeader(object):
    def __init__(self, *args, **kwargs):
        self.headers = {}
        super(HTTPHeader, self).__init__()

    def set(self, name, value):
        if name == 'Set-Cookie':
            if not self.headers.has_key(name):
                self.headers[name] = []
            self.headers[name].append(value)

        else:
            self.headers[name] = value

    def clear(self, name):
        if self.headers.has_key(name):
            del self.headers[name]

    def get(self, name, default=None):
        if self.headers.has_key(name):
            return self.headers[name]
        return default

    def __getitem__(self, name, default=None):
        return self.get(name, default)

    def __setitem__(self, name, value):
        self.set(name, value)

    def __delitem__(self, name):
        self.clear(name)

    def raw_headers(self):
        raw_headers = []

        for key in self.headers:
            if type(self.headers[key]) == types.ListType:
                for v in self.headers[key]:
                    raw_headers.append((key, v))

            else:
                raw_headers.append((key, self.headers[key]))

        return raw_headers