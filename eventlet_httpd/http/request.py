# coding=utf-8
from eventlet_httpd.http.parser.parser import parse_querystring, parse_multipart


class HTTPRequest(object):
    def __init__(self, *args, **kwargs):
        super(HTTPRequest, self).__init__()
        self.environ = kwargs.get('environ')
        self.url = self._parse_url()
        self.method = self.environ.get('REQUEST_METHOD', 'GET')
        self.upload_handler_class = None
        self._POST = None
        self._GET = None
        self._FILES = None

    def _parse_url(self):
        url = self.environ.get('PATH_INFO')
        if url != '/' and url.endswith('/'):
            url = url.rstrip('/')
        return url

    @property
    def GET(self):
        if self._GET is None:
            self.load_get()
        return self._GET

    @property
    def POST(self):
        if self._POST is None:
            self.load_post_and_files()
        return self._POST

    @property
    def FILES(self):
        if self._FILES is None:
            self.load_post_and_files()

        return self._FILES

    def set_upload_handler_class(self, upload_handler_class):
        self.upload_handler_class = upload_handler_class

    def load_post_and_files(self):
        self._FILES = {}
        self._POST = {}
        if self.method == 'POST':
            self._POST, self._FILES = parse_multipart(self.environ,
                                                      handler_class=self.upload_handler_class)

    def load_get(self):
        self._GET = parse_querystring(self.environ.get('QUERY_STRING', ''))