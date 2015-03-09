# coding=utf-8
import re
from wsgiref.headers import Headers
from eventlet_httpd import sleep
from eventlet_httpd.core.files.upload_handler import SmartyUploadHandler, MemoryUploadHandler
from eventlet_httpd.http.parser.header import parse_options




def tob(data, enc='utf8'):
    return data.encode(enc) if isinstance(data, unicode) else data





class MultipartError(ValueError):
    pass


class MultipartParser(object):
    def __init__(self, stream, boundary, content_length=-1, memory_limit=2*1024, charset='latin1', upload_handler_class=None, callbacks=None):
        """
            Parse a multipart/form-data byte stream. This object is an iterator
            over the parts of the message.

            :param stream: A file-like stream. Must implement ``.read(size)``.
            :param boundary: The multipart boundary as a byte string.
            :param content_length: The maximum number of bytes to read.
        """
        self.stream, self.boundary = stream, boundary
        self.content_length = content_length
        self.memory_limit = memory_limit
        self.charset = charset
        if self.memory_limit - 6 < len(boundary):  # "--boundary--\r\n"
            raise MultipartError('Boundary does not fit into buffer_size.')
        self._done = []
        self._part_iter = None
        self.upload_handler_class = upload_handler_class
        self.callbacks = callbacks

    def __iter__(self):
        """
        Iterate over the parts of the multipart message.
        """
        if not self._part_iter:
            self._part_iter = self._iterparse()

        for part in self._done:
            yield part

        for part in self._part_iter:
            self._done.append(part)
            yield part

    def parts(self):
        """
        Returns a list with all parts of the multipart message.
        """
        return list(iter(self))

    def get(self, name, default=None):
        """
        Return the first part with that name or a default value (None).
        """
        for part in self:
            if name == part.name:
                return part
        return default

    def get_all(self, name):
        """
        Return a list of parts with that name.
        """
        return [p for p in self if p.name == name]

    def _lineiter(self):
        """
        Iterate over a binary file-like object line by line. Each line is
        returned as a (line, line_ending) tuple. If the line does not fit
        into self.buffer_size, line_ending is empty and the rest of the line
        is returned with the next iteration.
        """
        read = self.stream.read
        max_read, max_buf = self.content_length, self.memory_limit
        _bcrnl = tob('\r\n')
        _bcr = _bcrnl[:1]
        _bnl = _bcrnl[1:]
        _bempty = _bcrnl[:0]  # b'rn'[:0] -> b''
        last_word = _bempty  # buffer for the last (partial) line

        while 1:
            data = read(max_buf if max_read < 0 else min(max_buf, max_read))
            max_read -= len(data)

            bytes_str = last_word + data
            lines = bytes_str.splitlines(True)
            len_first_line = len(lines[0])
            # be sure that the first line does not become too big
            if len_first_line > self.memory_limit:
                # at the same time don't split a '\r\n' accidentally
                if len_first_line == self.memory_limit + 1 and lines[0].endswith(_bcrnl):
                    split_pos = self.memory_limit - 1
                else:
                    split_pos = self.memory_limit

                lines[:1] = [
                    lines[0][:split_pos],
                    lines[0][split_pos:]
                ]

            if data:
                last_word = lines[-1]
                lines = lines[:-1]

            for line in lines:
                if line.endswith(_bcrnl):
                    yield line[:-2], _bcrnl

                elif line.endswith(_bnl):
                    yield line[:-1], _bnl

                elif line.endswith(_bcr):
                    yield line[:-1], _bcr

                else:
                    yield line, _bempty

                sleep(0.01)

            if not data:
                break

    def _iterparse(self):
        lines, line = self._lineiter(), ''
        separator = tob('--') + tob(self.boundary)
        terminator = tob('--') + tob(self.boundary) + tob('--')
        # Consume first boundary. Ignore leading blank lines
        for line, nl in lines:
            if line:
                break

        if line != separator:
            raise MultipartError("Stream does not start with boundary")

        # For each part in stream...
        is_tail = False  # True if the last line was incomplete (cutted)
        opts = {
            'memory_limit': self.memory_limit,
            'charset': self.charset,
            'upload_handler': self.upload_handler_class(),
            'callbacks': self.callbacks
        }
        part = MultipartPart(**opts)
        for line, nl in lines:
            if line == terminator and not is_tail:
                part.finish_body()
                yield part
                break

            elif line == separator and not is_tail:
                part.finish_body()
                yield part
                part = MultipartPart(**opts)

            else:
                # The next line continues this one
                is_tail = not nl
                part.feed(line, nl)

        if line != terminator:
            part.clear()
            raise MultipartError("Unexpected end of multipart stream.")


class MultipartPart(object):
    def __init__(self, memory_limit=2*1024*1024, charset='latin1', upload_handler=None):
        self.headers_list = []
        self.headers = None
        self.size = 0
        self.options = {}
        self._buf = tob('')
        self.disposition, self.name, self.filename = None, None, None
        self.content_type, self.charset = None, charset
        self.memory_limit = memory_limit
        self.upload_handler = None
        self.set_upload_handler(handler=upload_handler)
        self.content_length = -1

    def set_upload_handler(self, handler):
        if handler is None:
            handler = SmartyUploadHandler(memory_limit=self.memory_limit)
        self.upload_handler = handler

    def feed(self, line, nl=''):
        if self.upload_handler.is_started():
            return self.write_body(line, nl)

        return self.write_header(line, nl)

    def write_header(self, line, nl):
        line = line.decode(self.charset or 'latin1')
        if not nl:
            raise MultipartError('Unexpected end of line in header.')

        if not line.strip():
            # blank line -> end of header segment
            self.finish_header()

        elif line[0] in ' \t' and self.headers_list:
            name, value = self.headers_list.pop()
            self.headers_list.append((name, value + line.strip()))

        else:
            if ':' not in line:
                raise MultipartError("Syntax error in header: No colon.")

            name, value = line.split(':', 1)
            self.headers_list.append((name.strip(), value.strip()))

    def write_body(self, line, nl):
        if not line and not nl:
            # This does not even flush the buffer
            return

        self.upload_handler.write(self._buf + line)
        self.size += len(line) + len(self._buf)
        self._buf = nl

        if 0 < self.content_length < self.size:
            raise MultipartError('Size of body exceeds Content-Length header.')

    def finish_header(self):
        self.headers = Headers(self.headers_list)

        ctype = self.headers.get('Content-Type', '')
        cdis = self.headers.get('Content-Disposition', '')
        if not cdis:
            raise MultipartError('Content-Disposition header is missing.')

        self.disposition, self.options = parse_options(cdis)
        self.content_type, options = parse_options(ctype)
        self.name = self.options.get('name')
        self.filename = self.options.get('filename')
        self.charset = options.get('charset') or self.charset
        self.content_length = int(self.headers.get('Content-Length', '-1'))
        self.upload_handler.start(self.name, filename=self.filename, size=self.content_length)

    def finish_body(self):
        self.upload_handler.seek(0)
        self.upload_handler.finish()

    @property
    def value(self):
        """
        Data decoded with the specified charset
        """
        if self.filename:
            self.upload_handler.seek(0)
            return self.upload_handler.file

        else:
            pos = self.upload_handler.tell()
            self.upload_handler.seek(0)
            val = self.upload_handler.read()
            self.upload_handler.seek(pos)
            return val.decode(self.charset)

    def clear(self):
        if self.upload_handler:
            self.upload_handler.clear()