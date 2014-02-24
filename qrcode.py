import MultipartPostHandler
import json
import urllib2

def scan(picfile):
    opener = urllib2.build_opener(MultipartPostHandler.MultipartPostHandler)
    opener.addheaders = [('User-Agent', 'Mozilla/5.0'),
               ('Referer', 'http://cli.im/deqr'),
               ('Accept' ,'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
               ('Accept-Language', 'zh-CN')]

    params = {'data' : open(picfile, 'rb'), 'url' : 'http://', 'type' : 'sxt', 'type' : 'up'}
    ret = json.loads(opener.open('http://cli.im/deqr/scan', params).read())
    return ret['result']

if __name__ == '__main__':
    print scan(r'z:/untitled.png')