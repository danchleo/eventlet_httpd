# coding=utf-8
import os
from eventlet_httpd.http import HTTPRequest
from eventlet_httpd.http import HTTPResponse, HttpResponse404, HttpResponse500
from eventlet_httpd.http.error import HttpError
from eventlet_httpd.core.router import Router
import eventlet
from eventlet import wsgi


class Application(object):
    def __init__(self, logger=None, debug=False, threads_size=300, max_requests=3096):
        super(Application, self).__init__()
        self.logger = logger
        self.router = Router()
        self.debug = debug
        self.host = None
        self.port = 8000
        self.threads_size = threads_size
        self.max_requests = max_requests
        self._set_eventlet_thread_size()

    def _set_eventlet_thread_size(self):
        os.environ['EVENTLET_THREADPOOL_SIZE'] = self.threads_size

    def log(self, msg):
        if self.logger:
            self.logger.write(msg)

    def handle(self, environ, start_response):
        try:
            request = HTTPRequest(environ=environ)
            route = self.router.search(request)

            if route is not None:
                self.log('From IP:%(client_ip)s access %(url)s(%(method)s) Start' % {
                    'method': request.method,
                    'url': request.url,
                    'client_ip': request.environ.get('REMOTE_ADDR', 'Unknown')
                })

                ret = route.execute(request)
                if isinstance(ret, HTTPResponse):
                    response = ret

                else:
                    response = HTTPResponse(content=ret)

            else:
                response = HttpResponse404()

        except HttpError as e:
            response = e.response

        except:
            import traceback
            error_msg = traceback.format_exc()
            self.log(error_msg)

            response = HttpResponse500()
            if self.debug:
                response._content = '<pre>%s</pre>' % error_msg

        return response.response(start_response=start_response, environ=environ)

    def run(self, host='0.0.0.0', port=8000, logger=None, debug=False, threads_size=300, max_requests=3096):
        self.logger = logger
        self.debug = debug
        self.bind(host, port)
        self.threads_size = threads_size
        self.max_requests = max_requests
        wsgi.server(eventlet.listen((self.host, self.port)), self.handle, max_size=self.max_requests)

    def bind(self, host, port=8000):
        self.host = host
        self.port = port