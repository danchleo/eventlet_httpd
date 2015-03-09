# coding=utf-8
import os
import eventlet
from eventlet import tpool
from eventlet import patcher


ASYNC_POOL = None
__all__ = ['asynchronous', 'asynchronous_timeout']


def get_async_pool():
    global ASYNC_POOL

    if not ASYNC_POOL:
        pool_size = os.environ.get('EVENTLET_HTTPD_POOL_SIZE', 1024)
        ASYNC_POOL = eventlet.GreenPool(size=pool_size)

    return ASYNC_POOL


class AsyncResult(object):
    def __init__(self):
        super(AsyncResult, self).__init__()
        self._result = None
        self._done = False
        self._lock = patcher.original('threading').RLock()

    @property
    def done(self):
        self._lock.acquire()
        _done = self._done
        self._lock.release()
        return _done

    @property
    def result(self):
        return self._result

    def set_result(self, value):
        self._lock.acquire()
        self._result = value
        self._done = True
        self._lock.release()


class AsyncTimeout(Exception):
    pass


def _asynchronous_timeout(timeout=None):
    def _asynchronous(func):
        def __asynchronous(*args, **kwargs):
            def __asynchronous_call(callback, *args, **kwargs):
                try:
                    result = func(*args, **kwargs)
                    callback(result)
                except Exception, e:
                    callback(e)

            pool = get_async_pool()
            result = AsyncResult()
            pool.spawn_n(tpool.execute, __asynchronous_call, lambda x: result.set_result(x), *args, **kwargs)

            _sleep = 0.2
            _using = 0
            while not result.done:
                if timeout and _using >= timeout:
                    raise AsyncTimeout()
                eventlet.sleep(_sleep)
                _using += _sleep
            return result.result

        return __asynchronous
    return _asynchronous


asynchronous = _asynchronous_timeout()
asynchronous_timeout = _asynchronous_timeout