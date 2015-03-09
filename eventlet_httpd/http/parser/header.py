# coding=utf-8
import re


_SPECIAL_WORDS = re.escape('()<>@,;:\\"/[]?={} \t')
_RE_SPECIAL_WORDS = re.compile('[%s]' % _SPECIAL_WORDS)
_QUOTED_STR = '"(?:\\\\.|[^"])*"'  # Quoted string
_VALUE_WORDS = '(?:[^%s]+|%s)' % (_SPECIAL_WORDS, _QUOTED_STR)  # Save or quoted string
_HEADER_OPTION = '(?:;|^)\s*([^%s]+)\s*=\s*(%s)' % (_SPECIAL_WORDS, _VALUE_WORDS)
_RE_HEADER_OPTION = re.compile(_HEADER_OPTION)  # key=value part of an Content-Type like header


def quote(val):
    if not _RE_SPECIAL_WORDS.search(val):
        return val
    return '"' + val.replace('\\', '\\\\').replace('"', '\\"') + '"'


def unquote(val):
    if val[0] == val[-1] == '"':
        val = val[1:-1]
        if val[1:3] == ':\\' or val[:2] == '\\\\':
            val = val.split('\\')[-1]  # fix ie6 bug: full path --> filename
        return val.replace('\\\\', '\\').replace('\\"', '"')
    return val


def parse_options(header, options=None):
    if ';' not in header:
        return header.lower().strip(), {}
    ctype, tail = header.split(';', 1)
    options = options or {}
    for match in _RE_HEADER_OPTION.finditer(tail):
        key = match.group(1).lower()
        value = unquote(match.group(2))
        options[key] = value
    return ctype, options