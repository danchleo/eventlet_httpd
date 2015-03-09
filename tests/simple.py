# coding=utf-8
import init
from eventlet_httpd import run, get


@get('/')
def test(request):
    return '123123132'


run()