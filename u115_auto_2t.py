#!/usr/bin/env python
# -*- coding: utf-8 -*-
#qpy:console
from hashlib import sha1, md5
import time
from urllib import urlencode
from urllib import quote
import random
import string
import json
import re
import uuid
import sys
import time
from u115_api import u115_api
from tempmail_ru import tempmail_ru
ANDROID_API_URL = 'http://pro.api.115.com'
model = 'GT-I9100'
os_ver = '2.3.4'
basedir = r'D:\Dev\Python\Workspace\reverse-works\115-android\115-Lixian-API'
reload(sys)
sys.setdefaultencoding('utf-8')
def print_(str):
    print(str.decode('utf-8'))

class u115_android_api(u115_api):
    def __init__(self):
        u115_api.__init__(self)
        self.http.header.update({'User-agent':'Dalvik/1.4.0 (Linux; U; Android %s; %s Build/%s)' % (os_ver, model, ''.join(random.sample(string.ascii_letters+string.digits, 5)))})

    def login(self, username, password):
        key = ''.join(random.sample(string.ascii_letters+string.digits, 13))
        #key = 'G1I5ONLDOdRST'
        #_time = str(1393150825950)
        vcode = key.upper()
        _time = str(int(time.time()))
        guid = str(uuid.uuid4())
        sign = md5(username+sha1(password).hexdigest()+_time+"115ud&52DaRBaew").hexdigest()
        password = sha1(sha1(sha1(password).hexdigest() + sha1(username).hexdigest()).hexdigest() + vcode).hexdigest()
        veri_code = ''
        data = urlencode({'sign' : sign, 'ssopw' : password, 'ssoext' : key, 'ssoid' : veri_code, 'ssoinfo' : '', 
                          'os_ver' : os_ver, 'device' : model, 'n_type' : 'wifi', 'account' : username,                               
                          'device_id' : guid, '_time' : _time, 'version' : '2.0', 'm_type' : model})
        resp, ret = self.http.post(ANDROID_API_URL + '/android/1.0/login' , data, setcookie = True)
        if not resp['status'] == 200:
            print_('115Android登陆失败:请求失败')
            return
        try:
            ret = json.loads(ret)
        except ValueError:
            print_('115Android登陆失败，返回非json')
            return False
        self.space = ret['sapce']['1']
        print 'size_total', self.space['size_total']
        if ret.has_key('error') and ret['error']:
            print_('115Android登陆失败:%s' % ret['error'].encode('utf-8'))
        else:
            print_('115Android登陆成功')

class u115_23333(u115_api):
    def get_reward(self, rw_type = 'get_client_login_space'):
        resp, ret = self.http.post('http://115.com/?ct=event&ac=%s' % rw_type, postdata = 't=%d' % time.time()*1000,\
            referer = 'http://115.com/event/2014/chunjie/?top')
        try:
            ret = json.loads(ret)
        except ValueError:
            return False
        if not ret['state']:
            print ret['err_msg']
            return ret['err_code']
        else:
            return 0

def batch_reg(cnt = 10, rand_pwd = False):
    if rand_pwd:
        pwd = ''.join(random.sample(string.ascii_letters+string.digits,10))
    else:
        pwd = 'hahaha115'
    tmr = tempmail_ru()
    outf = open(basedir + r'\reg.txt','a')
    for uname in tmr.pool():
        if cnt <= 0 :
            break
        print uname
        u115_pc = u115_23333()
        if not u115_pc.siginup(uname, passwd = pwd):
            continue
        time.sleep(8)
        trytime = 3
        while trytime > 0:
            mails = tmr.get_mail()
            if mails:
                break
            print('no mails, sleep 3')
            trytime -= 1
            time.sleep(3)
        actvurl = re.findall('a href=\"(http://passport.115.com.*?)\"\>',mails[0]['mail_text_only'])[0]
        u115_pc.http.get(actvurl)
        u115_pc = u115_23333()
        u115_pc.login(uname, pwd)
        outf.write('%s,%s\n' % (uname,pwd))
        outf.flush()
        #open(basedir + r'\got.txt','a').write(uname)
        cnt -= 1
    outf.close()

def batch_get():
    acc = open(basedir + r'\reg.txt').readlines()
    done = open(basedir + r'\got.txt').readlines()
    outf = open(basedir + r'\got.txt','a')
    done = map(lambda x:x.rstrip('\n').rstrip('\r').rstrip(',hahaha115'), done)
    acc = map(lambda x:x.rstrip('\n').rstrip('\r').rstrip(',hahaha115'), acc)
    for l in acc:
        if l in done or not l:
            continue
        l = l.split(',')
        if len(l) == 1:
            uname, pwd = l[0], 'hahaha115'
        else:
            uname, pwd = l
        print uname
        u115_android = u115_android_api()
        u115_android.login(uname, pwd)
        if u115_android.space['byte_size_total'] > 2210018371829:
            outf.write('%s,%s\n' % (uname,pwd))
            outf.flush()
            print uname, 'done'
            time.sleep(5)
            continue
        time.sleep(10)
        u115_pc = u115_23333()
        u115_pc.login(uname, pwd)
        trytime = 3
        while trytime > 0:
            code = u115_pc.get_reward()
            if not code or code==200072:
                outf.write('%s,%s\n' % (uname,pwd))
                outf.flush()
                print uname, 'done'
                time.sleep(5)
                break
            trytime -= 1
            time.sleep(10)
    outf.close()

if __name__ == '__main__':
    #u115_android_api().login('nahof@rainmail.biz', 'hahaha115')
    # u115_pc.login('rerudag@mailblog.biz', 'hahaha115')
    # u115_pc.get_reward()
    # sys.exit(0)
    batch_reg(rand_pwd=True)
    #batch_get()