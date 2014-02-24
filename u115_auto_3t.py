#!/usr/bin/env python
# -*- coding: utf-8 -*-
#qpy:console
from hashlib import sha1, md5
import time
from urllib import urlencode
from urllib import quote
import urllib2
import random
import string
import json
import re
import uuid
import sys
import time
import threading
from u115_api import u115_api
from tempmail_ru import tempmail_ru
import qrcode

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
            return
        if ret.has_key('error') and ret['error']:
            print_('115Android登陆失败:%s' % ret['error'].encode('utf-8'))
            return
        else:
            print_('115Android登陆成功')
        self.uid = ret['user_id']
        self.ssoinfo = ret['ssoinfo']
        self.source = ret['resource']
        if not ret.has_key('sapce'):
            print_('邮箱未验证')
            print ret
            return
        self.space = ret['sapce']['1']
        print 'size_total', self.space['size_total']
        return True

    def qrcode(self, fname = r'z:/123.png'):
        #http://115.com/scan/xxxxx
        barinfo = qrcode.scan(fname)['ScanResult'][20:]
        uri = '/android/1.0/scan/prompt?ssoinfo=%s&user_id=%s&source=%s&info=%s' % (
            quote(self.ssoinfo), self.uid, quote(self.source), quote(barinfo)
            )
        resp, ret = self.http.get(ANDROID_API_URL + uri)
        ret = json.loads(ret)
        if not ret['state']:
            print_('扫描登陆失败:%s' % ret['error'])
        resp, ret = self.http.get(ret['data']['do_url'])
        ret = json.loads(ret)
        if not ret['state']:
            print_('登陆失败:%s' % ret['error'])
        print '115Android:'+ret['data']['tip_txt']
        #GET /android/1.0/scan/slogin?user_id=334967048&source=%7B%22email%22%3A%22nahof%40rainmail.biz%22%2C%22user_id%22%3A%22334967048%22%2C%22user_name%22%3A%22334967048%22%2C%22_sign%22%3A%220653a5027776f5d2ad906f62686143f6%22%7D&key=a35a3c41f84d8e1e816bbf772104e918&uid=[\'597fc598fb5e74f197eed0c93c5944285d2a3ffe\'] HTTP/1.1
        #source = {"email":"ffffonion@163.com","user_id":"14323462","user_name":"ffffonion","_sign":"44f5bdfe9bb72fac6e31d05f53f78715"} double urlencode

class u115_23333(u115_api):
    def get_reward(self, rw_type = 'get_client_login_space'):
        #get_five_login_space, get_qr_login_space
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
            print_('领取成功')
            return 0

    def get_qrcode(self, fname = r'z:/123.png'):
        ret = urllib2.urlopen('http://115.com').read()
        self.qr_uid = re.findall('var uid = "([\w\d]+)";', ret)[0]
        self.qr_sign = re.findall('var sign = "([\w\d]+)";', ret)[0]
        self.qr_time = re.findall('var time = "([\w\d]+)";', ret)[0]
        ret = urllib2.urlopen('http://www.115.com/?ct=scan&ac=qrcode&uid=%s&_t=%d' % (
                        self.qr_uid, time.time()*1000
                        )).read()
        open(fname,'wb').write(ret)
        print_('已保存二维码%s' % fname)

    def login_qrcode(self):

        resp, ret = self.http.get('http://msg.115.com/proapi/anonymous.php?ac=signin&user_id=%s&sign=%s&time=%s&_t=%d' % (
                        self.qr_uid, self.qr_sign, self.qr_time, time.time()*1000
                        ))
        ret = json.loads(ret)
        url = ret['url']
        s = ret['session_id']
        print_('已发送查询……')
        #urllib2.urlopen('%s/chat/bridge?namespace=Core.DataAccess&api=ConnectAPI&_t=v4' % url).read()
        ret = urllib2.urlopen('%s/chat/r?VER=2&c=b3&s=%s&_t=%d' % (
                            url, s, time.time()*1000)
                    , timeout = 66).read()
        for j in ret.split(' '):
            jo = re.findall('\[(.+)\]', j)
            if jo:
                jo = json.loads(jo[0])
                d = jo['p'][0]
                if d['status'] == 1002:
                    key = d['key']
                    break
        print_('正在二维码登陆')
        self.http.get('http://passport.115.com/?ct=login&ac=qrcode&key=%s' % key ,setcookie = True)
        self.http.get('http://115.com')
        print_('已退出')
            #1000 expired 1001 not-ready 1002 done

def batch_reg(cnt = 10, rand_pwd = False):
    if not rand_pwd:
        pwd = 'hahaha115'
    tmr = tempmail_ru()
    outf = open(basedir + r'\reg.txt','a')
    for uname in tmr.pool():
        if cnt <= 0 :
            break
        if uname.endswith('postalmail.biz'):#注册失败:系统限制注册,请联系客服！
            continue
        print uname
        if rand_pwd:
            pwd = ''.join(random.sample(string.ascii_letters+string.digits,random.randint(7,12)))
        u115_pc = u115_23333()
        if not u115_pc.siginup(uname, passwd = pwd):
            time.sleep(3)
            continue
        time.sleep(8)
        trytime = 5
        while trytime > 0:
            mails = tmr.get_mail()
            if mails:
                break
            print('no mails, sleep')
            trytime -= 1
            time.sleep(5 * (5 - trytime))
        actvurl = re.findall('a href=\"(http://passport.115.com.*?)\"\>',mails[0]['mail_text_only'])[0]
        u115_pc.http.get(actvurl)
        u115_pc = u115_23333()
        u115_pc.login(uname, pwd)
        outf.write('%s,%s\n' % (uname,pwd))
        outf.flush()
        #open(basedir + r'\got.txt','a').write(uname)
        cnt -= 1
        print('-'*25)
    outf.close()

def batch_get():
    acc = open(basedir + r'\reg.txt').readlines()
    done = open(basedir + r'\got.txt').readlines()
    outf = open(basedir + r'\got.txt','a')
    done = map(lambda x:x.rstrip('\n').rstrip('\r').rstrip(',hahaha115'), done)
    acc = map(lambda x:x.rstrip('\n').rstrip('\r').rstrip(',hahaha115'), acc)
    err_cnt = 0
    for l in acc[::-1]:
        if l in done or not l:
            continue
        err_cnt += 1
        l = l.split(',')
        if len(l) == 1:
            uname, pwd = l[0], 'hahaha115'
        else:
            uname, pwd = l
        print uname
        u115_android = u115_android_api()
        if not u115_android.login(uname, pwd):
            continue
        if u115_android.space['byte_size_total'] > 2210018371829:
            outf.write('%s,%s\n' % (uname,pwd))
            outf.flush()
            print uname, 'done'
            time.sleep(5)
            continue
        time.sleep(10)
        u115_pc = u115_23333()
        u115_pc.login(uname, pwd)
        trytime = 1
        while trytime > 0:
            code = u115_pc.get_reward()
            if not code or code==200072:
                outf.write('%s,%s\n' % (uname,pwd))
                outf.flush()
                print uname, 'done'
                time.sleep(5)
                err_cnt -= 1
                break
            trytime -= 1
            time.sleep(10)
        print('-'*25)
    outf.close()
    print_('错误:%d个' % err_cnt)

def verify():
    done = open(basedir + r'\jibun.txt').readlines()
    done = map(lambda x:x.rstrip('\n').rstrip('\r'), done)
    for l in done:
        uname,pwd= l.split(',')
        u115_android = u115_android_api()
        u115_android.login(uname, pwd)
        if u115_android.space['byte_size_total'] <= 2210018371829:
            print uname, 'error!'
        time.sleep(2.718281828)

def batch_qr():
    acc = open(basedir + r'\got.txt').readlines()
    done = open(basedir + r'\got3.txt').readlines()
    outf = open(basedir + r'\got3.txt','a')
    done = map(lambda x:x.rstrip('\n').rstrip('\r'), done)
    acc = map(lambda x:x.rstrip('\n').rstrip('\r'), acc)
    random.shuffle(acc)
    for l in acc:
        if l in done or not l:
            continue
        uname, pwd = l.split(',')
        print uname
        u115_android=u115_android_api()
        u115_android.login(uname, pwd)
        if u115_android.space['byte_size_total'] > 3000000000000:
            outf.write('%s,%s\n' % (uname,pwd))
            outf.flush()
            print uname, 'done'
            time.sleep(5)
            continue
        trytime=3
        qrpic = r'z:/%s.png' % ''.join(random.sample(string.ascii_letters+string.digits,5))
        while trytime >0:
            try:
                u115_pc=u115_23333()
                u115_pc.get_qrcode(fname = qrpic)
            except IndexError:
                trytime -= 1
                time.sleep(5)
                print('no uid, retrying')
                continue
            else:
                break
        a = threading.Thread(target = u115_pc.login_qrcode, args = (), name = 'thread-web-login') 
        a.setDaemon(True)
        a.start()
        u115_android.qrcode(fname = qrpic)
        a.join()
        u115_pc=u115_23333()
        u115_pc.login(uname, pwd)
        code=u115_pc.get_reward('get_qr_login_space')
        if not code or code ==200072:
            outf.write('%s,%s\n' % (uname, pwd))
        print('-'*25)
    outf.flush()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'r':
            batch_reg(rand_pwd=True)
        elif sys.argv[1] == 'g':
            batch_get()
        elif sys.argv[1] == 'v':
            verify()
        elif sys.argv[1] == 'q':
            batch_qr()
    else:
        print('r:reg\ng:get rewards\nv:verify\nq:qrcode_login')