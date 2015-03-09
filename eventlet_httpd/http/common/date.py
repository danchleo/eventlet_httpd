# coding=utf-8
import re
import calendar
import time
import datetime


MONTHS = 'jan feb mar apr may jun jul aug sep oct nov dec'.split()
__D = r'(?P<day>\d{2})'
__D2 = r'(?P<day>[ \d]\d)'
__M = r'(?P<mon>\w{3})'
__Y = r'(?P<year>\d{4})'
__Y2 = r'(?P<year>\d{2})'
__T = r'(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})'
RFC1123_DATE = re.compile(r'^\w{3}, %s %s %s %s GMT$' % (__D, __M, __Y, __T))
RFC850_DATE = re.compile(r'^\w{6,9}, %s-%s-%s %s GMT$' % (__D, __M, __Y2, __T))
ASCTIME_DATE = re.compile(r'^\w{3} %s %s %s %s$' % (__M, __D2, __T, __Y))
ISO_DATE_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'



def http_date(timestamp):
    #Wed, 17 Jul 2013 06:05:18 GMT
    global ISO_DATE_FORMAT
    return time.strftime(ISO_DATE_FORMAT, time.gmtime(timestamp))


def parse_http_date(date):
    """
    Parses a date format as specified by HTTP RFC2616 section 3.3.1.
    """
    global RFC1123_DATE, RFC850_DATE, ASCTIME_DATE
    for regex in RFC1123_DATE, RFC850_DATE, ASCTIME_DATE:
        m = regex.match(date)
        if m is not None:
            break
    else:
        raise ValueError("%r is not in a valid HTTP date format" % date)

    try:
        year = int(m.group('year'))
        if year < 100:
            if year < 70:
                year += 2000
            else:
                year += 1900
        month = MONTHS.index(m.group('mon').lower()) + 1
        day = int(m.group('day'))
        hour = int(m.group('hour'))
        minute = int(m.group('minute'))
        sec = int(m.group('sec'))
        result = datetime.datetime(year, month, day, hour, minute, sec)
        return calendar.timegm(result.utctimetuple())

    except Exception:
        raise ValueError("%r is not a valid date" % date)