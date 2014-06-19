#coding:utf-8
import json
import re
import time
import httplib2
import StringIO
import base64
import random_code
import os
bksjw='http://bksjw.hust.edu.cn/'
hub='http://hub.hust.edu.cn/'
uname='U201214862'
pwd='jimchen012249'
#=httplib2.Http(proxy_info=httplib2.ProxyInfo(proxy_type=httplib2.socks.PROXY_TYPE_HTTP_NO_TUNNEL, proxy_host='192.168.124.1', proxy_port=23300))
h=httplib2.Http()
h.follow_redirects = False
header_yay={'Connection':' keep-alive',
'Cache-Control':' no-cache',
'Accept':' text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Pragma':' no-cache',
'User-Agent':' Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/538.40 (KHTML, like Gecko) Chrome/30.1.2551.0 Safari/538.40',
'DNT':' 1',
'Accept-Language':' zh-CN'}

def new_login():
    #initial session
    resp,ct=h.request('{0}index.jsp'.format(bksjw),headers=header_yay)
    print resp
    cookie=resp['set-cookie'].replace(' Path=/, ','').replace(' path=/','')+'usertype=xs'
    print('Session:\n%s'%cookie)
    header_yay.update({'Cookie':cookie})
    header_yay.update({'Referer':'http://hub.hust.edu.cn/index.jsp'})
    #get index page
    h.request('{0}indexinfo'.format(bksjw),headers=header_yay)
    resp,ct=h.request('{0}index.jsp'.format(bksjw),headers=header_yay)
    print resp
    servname=re.findall('app\d+.dc.hust.edu.cn',ct)[0]
    #get random key
    resp,ct=h.request('{0}randomKey.action?username={1}&time={2}'.format(
            bksjw,uname,'%d'%(time.time()*1000)
        ),headers=header_yay)
    print resp
    key1,key2=json.loads(ct)
    #get random image
    resp,ct=h.request('{0}randomImage.action?k1={1}&k2={2}&uno={3}&time={4}'.format(
            bksjw,key1,key2,uname,'%d'%(time.time()*1000)
        ),headers=header_yay)
    #analyze the code
    code=random_code.get_code(StringIO.StringIO(ct))
    print('code:%s'%code)
    #do login
    body='usertype=xs&username={0}&password={1}&'\
    'rand={2}&ln={3}&random_key1={4}&random_key2={5}&'\
    'submit=%E7%AB%8B%E5%8D%B3%E7%99%BB%E5%BD%95'.format(
        uname,base64.encodestring(pwd).replace('=','%3D').strip('\n'),
        code,servname,key1,key2)
    _h=header_yay
    _h.update({'Content-Type': 'application/x-www-form-urlencoded'})
    resp,ct=h.request('{0}hublogin.action'.format(bksjw),method='POST',body=body,headers=_h)
    #test result
    if resp['location']=='{0}indexinfo'.format(bksjw):#failed
        h.request('{0}indexinfo'.format(bksjw),headers=header_yay)
        resp,ct=h.request('{0}index.jsp'.format(bksjw),headers=header_yay)
        #print ct
        print(re.findall('消息：.+',ct)[0].strip('\n').decode('utf-8').encode('gbk'))
        os._exit(0)
    else:#succeed
        open('.saved_session','w').write(cookie)
        return cookie

def auth():
#    if os.path.exists('.saved_session'):
#        cookie=open('.saved_session').read()
#        header_yay.update({'Cookie':cookie})
#    else:
#        cookie=new_login()
    cookie = new_login()
    header_yay.update({'Cookie':cookie})
    while True:#make sure session is correct. this loop will run at most twice times
        h.request('{0}hub.jsp'.format(bksjw),headers=header_yay)
        h.request('{0}frames/top.jsp'.format(bksjw),headers=header_yay)
        resp,ct=h.request('{0}frames/body_left.jsp'.format(bksjw),headers=header_yay)
        h.request('{0}frames/body.jsp'.format(bksjw),headers=header_yay)
        try:
            print(re.findall('欢迎 (.+) 登录',ct)[0].decode('utf-8'))
        except IndexError:#expired
            cookie=new_login()
            header_yay.update({'Cookie':cookie})
        else:
            break

if __name__=='__main__':
   auth()
#till now we can use header_yay to do anything

