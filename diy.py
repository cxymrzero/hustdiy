#coding:utf-8
import web
import json
import re
import time
import httplib2
import StringIO
import base64
import random_code
import os
import requests

import MySQLdb

#config
urls = (
    '/', 'index',
    '/login', 'login',
    '/msg', 'msg',
    '/gender', 'gender',
    '/main', 'main',
    '/femain', 'femain'
#    '/getPic', 'getPic'
)

render = web.template.render('resource')
app = web.application(urls, globals())
#web.config.debug = False
#session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'uid':0})
#session
if web.config.get('_session') is None:
    session = web.session.Session(app, web.session.DiskStore('sessions'), {'uid': 0})
    web.config._session = session
else:
    session = web.config._session

bksjw='http://bksjw.hust.edu.cn/'
hub='http://hub.hust.edu.cn/'
#=httplib2.Http(proxy_info=httplib2.ProxyInfo(proxy_type=httplib2.socks.PROXY_TYPE_HTTP_NO_TUNNEL, proxy_host='192.168.124.1', proxy_port=23300))
h=httplib2.Http()
h.follow_redirects = False
header_yay={'Connection':' keep-alive',
'Cache-Control':' no-cache',
'Accept':' text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Pragma':' no-cche',
'User-Agent':' Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/538.40 (KHTML, like Gecko) Chrome/30.1.2551.0 Safari/538.40',
'DNT':' 1',
'Accept-Language':' zh-CN'}
s = requests.Session()
queryCET = 'http://bksjw.hust.edu.cn/aam/slj/WydjksBaoKao_initPage.action?cdbh=631'
queryReadyScore = 'http://bksjw.hust.edu.cn/aam/score/QueryScoreByStudent_readyToQuery.action?cdbh=225'
queryScore = 'http://bksjw.hust.edu.cn/aam/score/QueryScoreByStudent_queryScore.action'
queryHub = 'http://bksjw.hust.edu.cn/frames/body_left.jsp'

db = web.database(dbn='mysql', user='root', pw='jimchen', db='hustdiy')

def new_login(uname, pwd):
    #initial session
    resp,ct=h.request('{0}index.jsp'.format(bksjw),headers=header_yay)
    cookie=resp['set-cookie'].replace(' Path=/, ','').replace(' path=/','')+'usertype=xs'
    print('Session:\n%s'%cookie)
    header_yay.update({'Cookie':cookie})
    #get index page
    h.request('{0}indexinfo'.format(bksjw),headers=header_yay)
    resp,ct=h.request('{0}index.jsp'.format(bksjw),headers=header_yay)
    servname=re.findall('app\d+.dc.hust.edu.cn',ct)[0]
    #get random key
    resp,ct=h.request('{0}randomKey.action?username={1}&time={2}'.format(
            bksjw,uname,'%d'%(time.time()*1000)
        ),headers=header_yay)
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

def auth(uname, pwd):
#    if os.path.exists('.saved_session'):
#        cookie=open('.saved_session').read()
#        header_yay.update({'Cookie':cookie})
#    else:
#        cookie=new_login()
    cookie = new_login(uname, pwd)
    header_yay.update({'Cookie':cookie})
    while True:#make sure session is correct. this loop will run at most twice times
        h.request('{0}hub.jsp'.format(bksjw),headers=header_yay)
        h.request('{0}frames/top.jsp'.format(bksjw),headers=header_yay)
        resp,ct=h.request('{0}frames/body_left.jsp'.format(bksjw),headers=header_yay)
        h.request('{0}frames/body.jsp'.format(bksjw),headers=header_yay)
        try:
            print(re.findall('欢迎 (.+) 登录',ct)[0].decode('utf-8'))
        except IndexError:#expired
            cookie=new_login(uname, pwd)
            header_yay.update({'Cookie':cookie})
        else:
            break

def getCET(s, query):
    r = s.get(query, headers=header_yay)
    #print r.text
    lst = re.findall('<td>(\d)</td>', r.text)
    return max(lst)

def getMajor(s, query):
    r = s.get(query, headers=header_yay)
    major = re.findall('<div>(.*)</div>', r.text)
    major = major[1].split(' ')[1]
    #print r.text
    return major

def getScoreParas(s, query, header):
    headerForScore = header
    headerForScore.update({'Referer':' http://bksjw.hust.edu.cn/frames/body_left.jsp'})
    r = s.get(query, headers=headerForScore)
    #print r.text
    lst = re.findall('<input type="hidden" (.*)/>', r.text)
    paras = {}
    paras['key1'] = re.findall('"(\d+)"', lst[0])[0]
    paras['key2'] = re.findall('value=(.*)', lst[1])[0].strip("\"")
    paras['type'] = 'zcj'
    paras['stuSfid'] = re.findall('value=(.*)', lst[3])[0].strip("\"")
    paras['xqselect'] = '20142' #随便选的，都OK
    #print paras['key2']
    #print paras['stuSfid']
    return paras

def getScore(s, query, header, paras):
    headerForScore = header
    headerForScore.update({'Referer':' '+queryReadyScore})
    r = s.post(query, data=paras, headers=headerForScore)
    #print r.text
    score = re.findall('\d\d\.\d\d', r.text)[-1]
#    if score>u'80':
#        print '哎哟，不错哦'
#    else:
#        print 'wuwuwu...'
    return score

def getSession():
    if web.config.get('_session') is None:
        session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'uid':0})
        web.config._session = session
        print web.config._session
        #print '{0}'.format(web.config._session.uid)
    else:
        #print '{0}'.format(web.config._session.uid)
        session = web.config._session
    return session


class index:
    def GET(self):
        return render.index()
        #return render.msg()      

class login:
    def POST(self):
        i = web.input()
        try:
            auth(i.username, i.psw)
        except:
            return render.index()
        s = requests.Session()
        uid = i.username
        #print session.uid
        #session = getSession()
        session.uid = uid
        print "session.uid!?:{0}".format(session.uid)
        print "{0}".format(web.config._session.uid)
        cet = getCET(s, queryCET).encode('utf-8')
        paras = getScoreParas(s, queryReadyScore, header_yay)
        score = getScore(s, queryScore, header_yay, paras)
        if score > u'88':
            score = 1
        elif score > u'84':
            score = 2
        elif score > u'80':
            score = 3
        elif score > u'70':
            score = 4
        else:
            score = 5
        major = getMajor(s, queryHub).encode('utf-8')
        myvar = dict(uid = uid)
        results = db.select('stu_info_1', myvar, where="id=$uid")
        if not results:
            db.insert('stu_info_1', id=uid, major=major, grades=score, cet=cet)
        print cet
        print score
        print major
        raise web.seeother('/gender')

class gender:
    def GET(self):
        return render.gender()

class main:
    def GET(self):
#        return render.main()
        return render.msg()
    def POST(self):
        return render.msg()

class femain:
    def GET(self):
        return render.femain()
    def POST(self):
        return 

#class genPic:
#    def GET(self):
#        return self.POST()
#    def POST(self):
#        #return render.msg()

class msg:
    def GET(self):
        return self.POST()
    def POST(self):
        i = web.input()
        print i.place
        print i.cantin
        print i.love
#        if session.get('uid') is not None:
#            print session.uid
#        else:
#            print "shabi youguale"
#        return 
        #session = getSession()
        #print session.uid
        print web.ctx.session.uid
        return

if __name__ == '__main__':
    app.run()
