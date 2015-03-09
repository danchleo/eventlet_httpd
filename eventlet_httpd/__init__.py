# coding=utf-8
import eventlet
from eventlet_httpd.core.application import Application
from functools import wraps


APP = None


def _get_app():
    global APP
    if not APP:
        APP = Application()

    return APP


def run(host='0.0.0.0', port=8000, logger=None, debug=False,
        threads_size=300, max_requests=3096):
    app = _get_app()
    app.run(host=host, port=port, logger=logger, debug=debug,
            threads_size=threads_size, max_requests=max_requests)


def _create_request_decorator(method):
    def _request_decorator(url, *dec_args, **dec_kwargs):
        def _dec(func):
            app = _get_app()
            methods = []
            if isinstance(method, str):
                methods = method.split(',')
            elif isinstance(method, list):
                methods = method

            for _method in methods:
                _method = _method.strip()
                if _method:
                    app.router.add(url, _method, func, *dec_args, **dec_kwargs)

            @wraps(func)
            def _wrap(request, *args, **kwargs):
                return func(request, *args, **kwargs)
            return _wrap
        return _dec
    return _request_decorator


def url_pattern(url, callback, *args, **kwargs):
    app = _get_app()
    app.router.add(url, '*', callback, *args, **kwargs)


route = _create_request_decorator('*')
post = _create_request_decorator('POST')
get = _create_request_decorator('GET')
put = _create_request_decorator('PUT')
sleep = eventlet.sleep