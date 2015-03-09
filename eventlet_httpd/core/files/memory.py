# coding=utf-8
from io import BytesIO
from eventlet_httpd.core.files import File


class MemoryFile(File):
    def __init__(self, *args, **kwargs):
        kwargs['fp'] = BytesIO()
        super(MemoryFile, self).__init__(*args, **kwargs)