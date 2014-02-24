#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
from urllib2 import HTTPError

headers_main = {'User-Agent': 'Mozilla/5.0'}
headers_post = {'Content-Type': 'application/x-www-form-urlencoded'}

urllib2.socket.setdefaulttimeout(60)

class http_request:

    def __init__(self, cookie = '', proxy = None):
            self.cookie = cookie
            self.header = headers_main
            if proxy:
                self.opener = urllib2.build_opener(urllib2.ProxyHandler(proxy))
            else:
                self.opener = None

    def post(self, uri, postdata = '', setcookie = False, referer = None):
        header = self.header
        header.update(headers_post)
        header.update({'Cookie' : self.cookie})
        if referer:
            header.update({'Referer' : referer})
        try:
            req = urllib2.Request('%s' % uri, postdata, header)
            if self.opener:
                fd = self.opener.open(req)
            else:
                fd = urllib2.urlopen(req)
            content = fd.read()
            if setcookie and 'Set-cookie' in fd.headers:
                self.cookie = ''
                #虽然不能很好...但是能用
                for i in range(0, len(fd.headers["Set-cookie"])):
                    self.cookie += fd.headers["Set-cookie"][i].replace(',', ';')
            resp = {'status' : 200}
            return resp, content
        except HTTPError, e:
            resp = {'status' : e.code}
            return resp, ''
        except Exception, e:
            import traceback; traceback.print_exc()
            resp = {'status' : 600}
            return resp, ''

    def get(self, uri, setcookie = False, referer = None):
        header = self.header
        header.update({'Cookie' : self.cookie})
        if referer:
            header.update({'Referer' : referer})
        try:
            req = urllib2.Request('%s' % uri, headers = header)
            fd = urllib2.urlopen(req)
            content = fd.read()
            if setcookie:
                self.cookie = ''
                #虽然不能很好...但是能用
                for i in range(0, len(fd.headers["Set-cookie"])):
                    self.cookie += fd.headers["Set-cookie"][i].replace(',', ';')
            resp = fd.headers
            resp = {'status' : 200}
            return resp, content
        except HTTPError, e:
            resp = {'status' : e.code}
            return resp, ''
        except Exception, e:
            import traceback; traceback.print_exc()
            resp = {'status' : 600}
            return resp, ''

if __name__ == "__main__":
    http = http_request()
    resp, ret = http.get("http://www.baidu.com")
    print ret