# coding=utf-8
import init
from eventlet_httpd import sleep
from eventlet_httpd.core.coroutine import asynchronous
from eventlet_httpd import url_pattern, run
from eventlet_httpd.core.view import View


class TestView(View):
    def get(self, request):
        return 'tes222t'

class TestLongView(View):
    @asynchronous
    def get(self, request):
        i = 0
        while i < 1000000000:
            i += 1
        return 'long'


url_pattern('/test2', TestView)
url_pattern('/long', TestLongView)
run(debug=True)
