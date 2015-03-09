# coding=utf-8
from eventlet_httpd.core.files.temp import TempFile
from eventlet_httpd.core.files.memory import MemoryFile


class UploadHandler(object):
    def __init__(self, *args, **kwargs):
        self.name = None
        self.filename = None
        self.size = None
        self._file = None
        self._started = False
        super(UploadHandler, self).__init__()

    def write(self, data):
        pass

    def read(self, size=None):
        pass

    def seek(self, pos):
        pass

    def is_started(self):
        return self._started

    def start(self, name, filename=None, size=None):
        self.name = name
        self.filename = filename
        self.size = size
        self._started = True

    def clear(self):
        pass

    def finish(self):
        pass

    def tell(self):
        return 0

    @property
    def file(self):
        return self._file


class MemoryUploadHandler(UploadHandler):
    def __init__(self, *args, **kwargs):
        super(MemoryUploadHandler, self).__init__(*args, **kwargs)
        self._file = MemoryFile(name=self.name)
        self._finished = False

    def finish(self):
        self._file.seek(0)
        self._finished = True

    def write(self, data):
        self._file.write(data)

    def read(self, size=None):
        if not self._finished:
            raise Exception('Upload process is not finished')

        if not size:
            return self._file.read()

        return self._file.read(size)

    def seek(self, pos):
        self._file.seek(pos)

    def clear(self):
        self._file.close()
        del self._file

    def tell(self):
        return self._file.tell()


class TemporaryUploadHandler(MemoryUploadHandler):
    def __init__(self, *args, **kwargs):
        super(MemoryUploadHandler, self).__init__(*args, **kwargs)
        self._file = TempFile(name=self.name)


class SmartyUploadHandler(MemoryUploadHandler):
    def __init__(self, memory_limit=2*1024*1024, *args, **kwargs):
        self._memory_limit = memory_limit
        super(SmartyUploadHandler, self).__init__(*args, **kwargs)

    def write(self, data):
        if self._file.tell() > self._memory_limit:
            self._file.seek(0)
            read_data = self._file.read()
            del self._file

            self._file = TempFile(name=self.name)
            self._file.write(read_data)

        self._file.write(data)