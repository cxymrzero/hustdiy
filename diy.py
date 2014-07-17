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
from subprocess import Popen, PIPE, STDOUT
from PIL import Image

import MySQLdb
from web.contrib.template import render_jinja

#config
urls = (
    '/', 'index',
    '/login', 'login',
    '/msg', 'msg',
    '/gender', 'gender',
    '/main', 'main',
    '/femain', 'femain',
   '/getMalePic', 'getMalePic',
   '/getFePic', 'getFePic',
    '/last', 'last',
    '/finalPic', 'finalPic'
)

#render = web.template.render('resource')
render = render_jinja(
        'resource',
        encoding = 'utf-8',
    )

app = web.application(urls, globals())
#web.config.debug = False
#session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'uid':0})
#session
if web.config.get('_session') is None:
    session = web.session.Session(app, web.session.DiskStore('sessions'),\
     {'uid': 0, 'color':'#444444', 'imgUrl':0})
    web.config._session = session
else:
    session = web.config._session

bksjw='http://bksjw.hust.edu.cn/'
hub='http://hub.hust.edu.cn/'
# uname='U201214862'
# pwd='jimchen012249'
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
s = requests.Session()
queryCET = 'http://bksjw.hust.edu.cn/aam/slj/WydjksBaoKao_initPage.action?cdbh=631'
queryReadyScore = 'http://bksjw.hust.edu.cn/aam/score/QueryScoreByStudent_readyToQuery.action?cdbh=225'
queryScore = 'http://bksjw.hust.edu.cn/aam/score/QueryScoreByStudent_queryScore.action'
queryHub = 'http://bksjw.hust.edu.cn/frames/body_left.jsp'
queryName = 'http://hub.hust.edu.cn/hub.jsp'

db = web.database(dbn='mysql', user='root', pw='jimchen', db='hustdiy')

def new_login(uname, pwd):
    header={'Connection':' keep-alive',
    'Cache-Control':' no-cache',
    'Accept':' text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Pragma':' no-cache',
    'User-Agent':' Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/538.40 (KHTML, like Gecko) Chrome/30.1.2551.0 Safari/538.40',
    'DNT':' 1',
    'Accept-Language':' zh-CN'}
    #initial session
    resp,ct=h.request('{0}index.jsp'.format(bksjw),headers=header)
    print resp
    print ct
    cookie=resp['set-cookie'].replace(' Path=/, ','').replace(' path=/','')+'usertype=xs'
    print('Session:\n%s'%cookie)
    header.update({'Cookie':cookie})
    #get index page
    h.request('{0}indexinfo'.format(bksjw),headers=header)
    resp,ct=h.request('{0}index.jsp'.format(bksjw),headers=header)
    print resp
    # print "ct=%s"%ct
    servname=re.findall('app\d+.dc.hust.edu.cn',ct)[0]
    #get random key
    header['Referer'] = "http://bksjw.hust.edu.cn/index.jsp"
    header['X-Requested-With'] = 'XMLHttpRequest'
    resp,ct=h.request('{0}randomKey.action?username={1}&time={2}'.format(
            bksjw,uname,'%d'%(time.time()*1000)
        ),headers=header)
    print resp
    key1,key2=json.loads(ct)
    #get random image
    resp,ct=h.request('{0}randomImage.action?k1={1}&k2={2}&uno={3}&time={4}'.format(
            bksjw,key1,key2,uname,'%d'%(time.time()*1000)
        ),headers=header)
    #analyze the code
    code=random_code.get_code(StringIO.StringIO(ct))
    print('code:%s'%code)
    #do login
    body='usertype=xs&username={0}&password={1}&'\
    'rand={2}&ln={3}&random_key1={4}&random_key2={5}&'\
    'submit=%E7%AB%8B%E5%8D%B3%E7%99%BB%E5%BD%95'.format(
        uname,base64.encodestring(pwd).replace('=','%3D').strip('\n'),
        code,servname,key1,key2)
    print 'body=%s'%body
    _h=header
    _h.update({'Content-Type': 'application/x-www-form-urlencoded'})
    # _h.update({'Referer': 'http://hub.hust.edu.cn/frames/kslogin.jsp?url=http://bksjw.hust.edu.cn/'})
    resp,ct=h.request('{0}hublogin.action'.format(bksjw),method='POST',body=body,headers=_h)
    print "ct=%s"%ct
    print "resp=%s\n"%resp
    #test result
    if resp['location']=='{0}indexinfo'.format(bksjw):#failed
        h.request('{0}indexinfo'.format(bksjw),headers=header_yay)
        resp,ct=h.request('{0}index.jsp'.format(bksjw),headers=header_yay)
        print 'ct=%s'%ct
        print(re.findall('消息：.+',ct)[0].strip('\n').decode('utf-8').encode('gbk'))
        os._exit(0)
    else:#succeed
        # open('.saved_session','w').write(cookie)
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
    major = major[0].split(' ')[1]
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

def getName(s, query, header):
    r = s.get(query, headers=header_yay)   
    print r.text 
    name = re.findall("0;'>(.+)</div>", r.text)[0]
    name = name.split(' ')[1]
    return name

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

#bg: 500*680
#flesh-male: 153*570
#flesh-female: 153*525

def genBg(color):
    # color is a (x, y, z) RGB tuple.
    if color == '-':
        color = (68, 68, 68)
    image = Image.new('RGB', (500, 680), color)
    image.load()
    return image

def openImg(imgUrl):
    # open once, use eternaly:)
    img = Image.open(imgUrl)
    img.load()
    return img

def stickBag(offsetX, offsetY, img, Bg):
    # bag and belt
    offsetX = 250-offsetX/2
    offsetY = 340+offsetY+30
    bg = Bg
    r,g,b,a = img.split()
    bg.paste(img, (offsetX, offsetY), mask=a)
    return bg

def stickFace(offsetX, offsetY, img, Flesh):
    '''
    stick hair, face, and glasses, return flesh with face
    '''
    offsetX = 76-offsetX/2
    offsetY = 285+offsetY
    flesh = Flesh
    # img = Image.open(imgUrl)
    # img.load()
    r,g,b,a = img.split()
    flesh.paste(img, (offsetX, offsetY), mask=a)
    return flesh

def stickCloth(offsetX, offsetY, img, Bg, f2b):
    '''
    stick suit and shoes
    '''
    offsetX = 76-offsetX/2+f2b[0]
    offsetY = 285+offsetY+f2b[1]
    r,g,b,a = img.split()
    bg = Bg
    bg.paste(img, (offsetX, offsetY), mask=a)
    return bg

def stickFlesh(Bg, Flesh, offsetX, offsetY):
    bg = Bg
    flesh = Flesh
    r,g,b,a = flesh.split()
    bg.paste(flesh, (offsetX, offsetY), mask=a)
    return bg

def stickBook(offsetX, offsetY, img, Bg, f2b):
    offsetX = 76+offsetX/2+f2b[0]
    offsetY = 285+offsetY+f2b[1]
    r,g,b,a = img.split()
    bg = Bg
    bg.paste(img, (offsetX, offsetY), mask=a)
    return bg

def stickBasketball(x, y, img, Bg, f2b):
    x = 76+x/2+f2b[0]-160
    y = 285+y+f2b[1]
    r,g,b,a = img.split()
    bg = Bg
    bg.paste(img, (x, y), mask=a)
    return bg

def stickPanel(x, y, img, Bg, f2b):
    x = 76+x/2+f2b[0]-30
    y = 285+y+f2b[1]-10
    r,g,b,a = img.split()
    bg = Bg
    bg.paste(img, (x, y), mask=a)
    return bg

def getPicSize(Pic):
    size = Pic.size
    return size

def stripAddr(addr):
    # write this because f2e is a f**king SB!!!
    if addr == '-':
        s = '-'
    else:
        lst = addr.split('/block-icons')
        s = ''.join(lst)
    return s


class index:
    def GET(self):
        return render.index(fail = 0)
        # return render.last()  
    def POST(self):
        web.seeother('/', absolute=True)    

class login:
    def GET(self):
        web.seeother('/', absolute=True)
    def POST(self):
        try:
            i = web.input()
            auth(i.username, i.psw)
            '''
            try:
                auth(i.username, i.psw)
            except:
                return render.index()
            '''
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
            name = getName(s, queryHub, header_yay).encode('utf-8')
            myvar = dict(uid = uid)
            results = db.select('stu_info_1', myvar, where="id=$uid")
            if not results:
                db.insert('stu_info_1', id=uid, major=major, grades=score, cet=cet, name=name)
                # print cet
                # print score
                # print major
                # print name
            #     raise web.seeother('/gender')
        except:
            return render.index(fail = 1)
        raise web.seeother('/gender')

# configure user login
class AuthBase:
    def __init__(self):
        if session.uid == 0:
            web.seeother('/', absolute=True)

class gender(AuthBase):
    def GET(self):
        return render.gender()
    def POST(self):
        web.seeother('/', absolute=True)

class main(AuthBase):
    def GET(self):
        return render.main()
        # return render.msg()
    def POST(self):
        # return render.msg()
        # proc = Popen(["phantomjs", "test.js"],stdout=PIPE, stderr=STDOUT)
        # return render.last()
        return render.msg()

class femain(AuthBase):
    def GET(self):
        return render.femain()
    def POST(self):
        # return render.last()
        return render.msg()

class getMalePic:
# class getPic:
   def GET(self):
        f2b = (173, 85) #flesh to background
        i = web.input()
        # print 'bag:%s'%i._bag
        # print 'belt:%s'%i._bagbelt
        # print 'prop:%s'%i._prop
        # print 'sex:%s'%i.sex
        # print i._bg
        session.color = i._bg
        bg = genBg(i._bg)
        try:
            if i._prop[-5] == '5': #It's a bag.
                bag = openImg('static/image/bag.png')
                x, y = getPicSize(bag)
                bg = stickBag(x, -152, bag, bg)
        except:
            pass
        # if i.sex == '1':
        #     flesh = openImg('static/image/male.png')
        # else:
        #     flesh = openImg('static/image/female.png')
        flesh = openImg('static/image/male.png')
        if i._hair != '-':
            hair = openImg(stripAddr(i._hair))
            x, y = getPicSize(hair)
            flesh = stickFace(x, -265, hair, flesh)
        if i._face != '-':
            face = openImg(stripAddr(i._face))
            x, y = getPicSize(face)
            flesh = stickFace(x, -220, face, flesh)
        if i._glass != '-':
            glass = openImg(stripAddr(i._glass))
            x, y = getPicSize(glass)
            flesh = stickFace(x, -210, glass, flesh)
        bg = stickFlesh(bg, flesh, 173, 85)
        if i._suit != '-':
            suit = openImg(stripAddr(i._suit))
            x, y = getPicSize(suit)
            bg = stickCloth(x, -151, suit, bg, f2b)
        if i._shoes != '-':
            shoes = openImg(stripAddr(i._shoes))
            x, y = getPicSize(shoes)
            bg = stickCloth(x, 245, shoes, bg, f2b)
        if i._prop != '-':
            num = int(i._prop[-5])
            if num == 1 or num == 3:
                prop = openImg(stripAddr(i._prop))
                x, y = getPicSize(prop)
                bg = stickBook(x, 20, prop, bg, f2b)
            elif num == 2:
                prop = openImg(stripAddr(i._prop))
                x, y = getPicSize(prop)
                bg = stickBasketball(x, 200, prop, bg, f2b)
            elif num == 4:
                prop = openImg(stripAddr(i._prop))
                x, y = getPicSize(prop)
                bg = stickPanel(x, -10, prop, bg, f2b)

        # if i._bag-belt != '-'
        try:
            if i._prop[-5] == '5': #It's a bag.
                belt = openImg('static/image/bag-belt.png')
                x, y = getPicSize(belt)
                bg = stickBag(x, -152, belt, bg)
        except:
            pass
        imgUrl = session.uid.join(['static/userimg/', '.png'])
        session.imgUrl = imgUrl
        bg = bg.crop((0, 100, 500, 680))
        try:
            # flesh.save('img/testbg.png')
            # bg.save(session.uid.join(['img/', '.png']))
            bg.save(imgUrl)
        except:
            os.mkdir('static/userimg')
            # flesh.save('img/testbg.png')
            # bg.save(session.uid.join(['img/', '.png']))
            bg.save(imgUrl)
       # return self.POST()
       # web.seeother('/', absolute=True)
        return render.msg(imgUrl=imgUrl)
   def POST(self):
        raise web.seeother('/', absolute=True)

       #return render.msg()

def stickFace2(x, y, img, Bg):
    '''
    stick hair, face, and glasses to bg.
    '''
    # offsetX = 76-offsetX/2
    # offsetY = 285+offsetY
    x = 250-x/2
    y = 262+y+77
    bg = Bg
    r,g,b,a = img.split()
    bg.paste(img, (x, y), mask=a)
    return bg

def stickCloth2(offsetX, offsetY, img, Bg, f2b):
    '''
    stick suit and shoes
    '''
    offsetX = 76-offsetX/2+f2b[0]
    offsetY = 262+offsetY+f2b[1]
    r,g,b,a = img.split()
    bg = Bg
    bg.paste(img, (offsetX, offsetY), mask=a)
    return bg

class getFePic:
# class getPic:
   def GET(self):
        f2b = (173, 77) #flesh to background
        i = web.input()
        # print 'bag:%s'%i._bag
        # print 'belt:%s'%i._bagbelt
        # print 'prop:%s'%i._prop
        # print 'sex:%s'%i.sex
        bg = genBg(i._bg)
        session.color = i._bg
        try:
            if i._prop[-5] == '5': #It's a bag.
                bag = openImg('static/image/bag.png')
                x, y = getPicSize(bag)
                bg = stickBag(x, -185, bag, bg)
        except:
            pass
        # if i.sex == '1':
        #     flesh = openImg('static/image/male.png')
        # else:
        #     flesh = openImg('static/image/female.png')
        flesh = openImg('static/image/female.png')
        bg = stickFlesh(bg, flesh, 173, 77)
        if i._face != '-':
            face = openImg(stripAddr(i._face))
            x, y = getPicSize(face)
            bg = stickFace2(x, -234, face, bg)
        if i._glass != '-':
            glass = openImg(stripAddr(i._glass))
            x, y = getPicSize(glass)
            bg = stickFace2(x, -223, glass, bg)
        if i._hair != '-':
            hair = openImg(stripAddr(i._hair))
            x, y = getPicSize(hair)
            bg = stickFace2(x, -275, hair, bg)
        if i._suit != '-':
            suit = openImg(stripAddr(i._suit))
            x, y = getPicSize(suit)
            bg = stickCloth2(x, -171, suit, bg, f2b)
        if i._shoes != '-':
            shoes = openImg(stripAddr(i._shoes))
            x, y = getPicSize(shoes)
            bg = stickCloth2(x, 230, shoes, bg, f2b)
        if i._prop != '-':
            num = int(i._prop[-5])
            if num == 1 or num == 3:
                prop = openImg(stripAddr(i._prop))
                x, y = getPicSize(prop)
                bg = stickBook(x, -3, prop, bg, f2b)
            elif num == 2:
                prop = openImg(stripAddr(i._prop))
                x, y = getPicSize(prop)
                bg = stickBasketball(x, 200-23, prop, bg, f2b)
            elif num == 4:
                prop = openImg(stripAddr(i._prop))
                x, y = getPicSize(prop)
                bg = stickPanel(x, -10-23, prop, bg, f2b)

        # if i._bag-belt != '-'
        try:
            if i._prop[-5] == '5': #It's a bag.
                belt = openImg('static/image/bag-belt.png')
                x, y = getPicSize(belt)
                bg = stickBag(x, -185, belt, bg)
        except:
            pass
        # imgUrl = session.uid.join(['img/', '.png'])
        bg = bg.crop((0, 50, 500, 630))
        imgUrl = session.uid.join(['static/userimg/', '.png'])
        session.imgUrl = imgUrl
        try:
            # flesh.save('img/testbg.png')
            bg.save(imgUrl)
        except:
            os.mkdir('static/userimg')
            # flesh.save('img/testbg.png')
            bg.save(imgUrl)
        return render.msg(imgUrl=imgUrl, fail=0)
   def POST(self):
        raise web.seeother('/', absolute=True)

class msg(AuthBase):
    def GET(self):
        web.seeother('/', absolute=True)
        # return render.index()
    def POST(self):
        i = web.input()
        try:
            print i.place
            print i.cantin
            print i.love
            print i.org
        except:
            return render.msg(imgUrl=session.imgUrl, fail=True)
#        if session.get('uid') is not None:
#            print session.uid
#        else:
#            print "shabi youguale"
#        return 
        #session = getSession()
        #print session.uid
        print session.uid
        myvar = dict(uid = session.uid)
        results = db.select('stu_info_2', myvar, where="id=$uid")
        if results:
            db.delete('stu_info_2', where="id=$uid", vars=myvar)
        db.insert('stu_info_2', id=session.uid, live=i.place, eat=i.cantin, love=i.love, org=i.org)
        return web.seeother('/last')

class last(AuthBase):
    def GET(self):
        myvar = dict(uid=session.uid)
        r1 = list(db.select('stu_info_1', myvar, where="id=$uid"))
        r2 = list(db.select('stu_info_2', myvar, where="id=$uid"))
        #print results1[0].major
        major = r1[0].major
        # if major == '计算机科学与技术学院'
        grades = r1[0].grades
        cet = r1[0].cet
        name = r1[0].name
        live = r2[0].live
        eat = r2[0].eat
        love = r2[0].love
        org = r2[0].org
        imgUrl = session.uid.join(['static/userimg/', '.png'])
        return render.last(major=major, grades=grades, cet=cet, \
            live=live, eat=eat, love=love, org=org, name=name, imgUrl=imgUrl, color=session.color)
    def POST(self):
        web.seeother('/', absolute=True)

class finalPic:
    def GET(self):
        filename = 'pic.png'
        filepath = 'static/userimg/' + session.uid + '.png'
        web.header("Content-Type","img/jpeg;charset=utf-8")
        web.header("Content-Disposition","attachment;filename=%s"%filename)
        f = open(filepath)
        return f.read()

if __name__ == '__main__':
    app.run()
