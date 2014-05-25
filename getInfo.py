#coding:utf-8
import hub
import requests
import re

hub.auth()
s = requests.Session()
hubHeader = hub.header_yay

queryCET = 'http://bksjw.hust.edu.cn/aam/slj/WydjksBaoKao_initPage.action?cdbh=631'
queryReadyScore = 'http://bksjw.hust.edu.cn/aam/score/QueryScoreByStudent_readyToQuery.action?cdbh=225'
queryScore = 'http://bksjw.hust.edu.cn/aam/score/QueryScoreByStudent_queryScore.action'
queryHub = 'http://bksjw.hust.edu.cn/frames/body_left.jsp'

def getCET(s, query):
    r = s.get(query, headers=hubHeader)
    #print r.text
    lst = re.findall('<td>(\d)</td>', r.text)
    return max(lst)

def getMajor(s, query):
    r = s.get(query, headers=hubHeader)
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
    if score>u'80':
        print '哎哟，不错哦'
    else:
        print 'wuwuwu...'
    print score

print getCET(s, queryCET)
print getMajor(s, queryHub)
postData = getScoreParas(s, queryReadyScore, hubHeader)
getScore(s, queryScore, hub.header_yay, postData)
