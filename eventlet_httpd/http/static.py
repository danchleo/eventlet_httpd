# coding=utf-8
import os
import re
import mimetypes
from eventlet_httpd.http.response import HTTPResponse
from eventlet_httpd.http.error import Http404, Http403, Http304
from eventlet_httpd.http.common import date


def get_expired_info(request):
    header = request.environ.get('HTTP_IF_MODIFIED_SINCE')
    if header:
        matches = re.match(r"^([^;]+)(; length=([0-9]+))?$", header, re.IGNORECASE)
        if matches:
            try:
                header_modified_time = date.http_date(matches.group(1))
                header_size = int(matches.group(3))
            except:
                return None

            return {
                'last_modified': header_modified_time,
                'size': header_size
            }


def resource_changed(request, filename):
    stat = os.stat(filename)
    expired_info = get_expired_info(request)

    if expired_info:
        if stat.st_size != expired_info['size']:
            return True

        if int(stat.st_mtime) > expired_info['last_modified']:
            return True

    return False


def serve_static(request, base_dir, filename, force_update=False):
    static_filename = os.path.abspath(os.path.join(base_dir, filename))
    if not static_filename.startswith(base_dir):
        raise Http403()

    if os.path.exists(static_filename):
        if not os.path.isdir(static_filename):
            file_stat = os.stat(static_filename)

            if not force_update and not resource_changed(request, static_filename):
                raise Http304()

            _t, encoding = mimetypes.guess_type(static_filename)

            response = HTTPResponse(content=open(static_filename, 'rb'))
            response.add_header('Last-Modified', date.http_date(file_stat.st_mtime))
            response.add_header('Content-Length', file_stat.st_size)
            if encoding:
                response.add_header('Content-Encoding', encoding)
            return response

    raise Http404()