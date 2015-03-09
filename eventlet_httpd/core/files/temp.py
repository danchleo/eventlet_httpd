# coding=utf-8
from tempfile import TemporaryFile
from eventlet_httpd.core.files import File

__all__ = ('TempFile', )


class TempFile(File):
    def __init__(self, *args, **kwargs):
        kwargs['fp'] = TemporaryFile(prefix='eventlet_httpd_upload_')
        super(TempFile, self).__init__(*args, **kwargs)