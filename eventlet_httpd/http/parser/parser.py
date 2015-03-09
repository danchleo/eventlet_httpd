# coding=utf-8
import urllib
import urlparse
from io import BytesIO
from eventlet_httpd.http.parser.multipart import MultipartError, MultipartParser
from eventlet_httpd.http.parser.header import parse_options


def parse_querystring(querystring):
    params = {}

    if querystring:
        params_tmp = querystring.split('&')

        for p in params_tmp:
            if p.find('=') > -1:
                tmp = p.partition('=')
                key = tmp[0].strip()
                value = tmp[2].strip()

                params[key] = urllib.unquote_plus(value)

    return params


def parse_multipart(environ, charset='utf8', strict=False, handler_class=None, memory_limit=2*1024*1024):
    posts, files = dict(), dict()
    try:
        if environ.get('REQUEST_METHOD', 'GET').upper() not in ('POST', 'PUT'):
            raise MultipartError("Request method other than POST or PUT.")

        content_length = int(environ.get('CONTENT_LENGTH', '-1'))
        content_type = environ.get('CONTENT_TYPE', '')

        if not content_type:
            raise MultipartError("Missing Content-Type header.")

        content_type, options = parse_options(content_type)
        stream = environ.get('wsgi.input') or BytesIO()

        if content_type == 'multipart/form-data':
            boundary = options.get('boundary', '')
            if not boundary:
                raise MultipartError("No boundary for multipart/form-data.")

            for part in MultipartParser(stream, boundary, content_length, memory_limit=memory_limit, charset=charset, **kwargs):
                # TODO: Big form-fields are in the files dict. really?
                if part.filename:
                    files[part.name] = part.value

                else:
                    posts[part.name] = part.value

        elif content_type in ('application/x-www-form-urlencoded',
                              'application/x-url-encoded'):
            if content_length > memory_limit:
                raise MultipartError("Request to big. Increase MAXMEM.")

            data = stream.read(memory_limit).decode(charset)
            if stream.read(1):
                # These is more that does not fit mem_limit
                raise MultipartError("Request to big. Increase MAXMEM.")

            data = urlparse.parse_qs(data, keep_blank_values=True)
            for key, values in data.iteritems():
                for value in values:
                    posts[key] = value

        else:
            raise MultipartError("Unsupported content type.")

    except MultipartError:
        if strict:
            raise

    return posts, files