# coding=utf-8


class File(object):
    def __init__(self, name, filename=None, path=None, fp=None, *args, **kwargs):
        self.name = name
        self.filename = filename
        self.fp = fp
        self.path = path
        super(File, self).__init__()

    def seek(self, cursor):
        self.fp.seek(cursor)

    def reset(self):
        self.fp.seek(0)

    def write(self, data):
        self.fp.write(data)

    def read(self, size=None):
        if not self.fp and not self.path:
            raise IOError('File is missing')

        if self.fp is None:
            self.fp = open(self.path, 'rb')
            self.reset()

        if size is not None:
            return self.fp.read(size)

        return self.fp.read()

    def close(self):
        if self.fp:
            self.fp.close()

    def tell(self):
        if self.fp:
            return self.fp.tell()

        return 0

    def __del__(self):
        self.close()

    def __str__(self):
        return self.read()