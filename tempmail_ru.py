#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import urllib2, cookielib
from http_request import http_request
from hashlib import md5
import json
import random
import string

class tempmail_ru():
    def __init__(self):
        self.http = http_request()
        self.has_cookie = False
        self.addr = None
        self.domain = None

    def pool(self):
        while True:
            self.new2()
            yield self.addr

    def new2(self):
        if self.addr:
            self._dispose()
        self._getnew()

    def new(self):
        if not self.domain:
            resp, ret = self.http.get('http://api.temp-mail.ru/request/domains/format/json')
            self.domain = json.loads(ret)
        self.addr = '%s%s' % (''.join(random.sample(string.ascii_letters,6)), random.choice(self.domain)) 

    def _getnew(self):
        #none api
        resp, ret = self.http.get('https://temp-mail.ru/', setcookie = not self.has_cookie, referer = 'https://temp-mail.ru/')
        self.addr = re.findall('\w+@\w+\.\w+', ret)[0]
        self.has_cookie = True

    def _dispose(self):
        #none api
        resp, ret = self.http.get('https://temp-mail.ru/option/delete', referer = 'https://temp-mail.ru/')

    def get_mail(self):
        resp, ret = self.http.get('http://api.temp-mail.ru/request/mail/id/%s/format/json/' % md5(self.addr).hexdigest())
        if resp['status'] == 404:
            return []
        ret = json.loads(ret)
        if isinstance(ret, list):
            return ret
        else:
            return []

if __name__ == '__main__':
    tmr = tempmail_ru()
    tmr.new()
    print tmr.addr
    # for addr in tmr.pool():
    #     print addr