#!/usr/bin/env python
''' Sparker5 nginx_uwsgi
    used for link nginx and webpy
    written by Sparker5.com
    Use:
        1:  import nginx_uwsgi in your webpy app file
        2:  set the SERVER_PORT, FOOT_PRINTS_PATH and ERROR_LOG_PATH in this file
        3:  setup your nginx
        4:  run the webpy app
'''
import os, sys, stat, socket, struct, StringIO, time, traceback, string
import web, web.wsgi

import site_helper as sh
SERVER_PORT         = sh.config.APP_PORT
ERROR_LOG_PATH      = sh.config.ERROR_LOG_PATH
FOOT_PRINTS_PATH    = sh.config.FOOT_LOG_PATH
IGNORE_SEND_EXCEPTION = True
ACCEPT_COOKIE_CHARS = '_-=:;\t\n\r!@#$%^&*., ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

allchars = string.maketrans('', '')
def makefilter(keep):
     delchars = allchars.translate(allchars, keep)
     def thefilter(s):
         return s.translate(allchars, delchars)
     return thefilter
justVowels = makefilter(ACCEPT_COOKIE_CHARS)

def parseRequest(sock):
    """
    This function receives request buffer from nginx, and then
    parses the buffer into a Python dictionary.
    """
    buf = sock.recv(4, socket.MSG_WAITALL)
    if len(buf) < 4:
        raise Exception()
    size = struct.unpack("=H", buf[1:3])[0]
    buf = sock.recv(size, socket.MSG_WAITALL)
    if len(buf) < size:
        raise Exception()

    request = {}
    i = 0
    while i < len(buf):
        size = struct.unpack("=H", buf[i:i+2])[0]
        k = buf[i+2:i+2+size]
        i = i + 2 + size
        size = struct.unpack("=H", buf[i:i+2])[0]
        v = buf[i+2:i+2+size]
        i = i + 2 + size
        request[k] = v

    if request.has_key("CONTENT_LENGTH") and \
            len(request["CONTENT_LENGTH"]) > 0:
        size = int(request["CONTENT_LENGTH"])
        data = sock.recv(size, socket.MSG_WAITALL)
        if len(data) < size:
            raise Exception()
        request["wsgi.input"] = StringIO.StringIO(data)

    request["request_log"] = {}

    return request

def quote(s_in):
    s_out = ""
    for c in s_in:
        if ord(c) <= 0x20 or ord(c) >= 0x7F or \
                c in ("\\", "'", '"'):
            s_out = s_out + "\\x{0:02x}".format( ord(c) )
        else:
            s_out = s_out + c
    return s_out

def nginxRunuwsgi(func):
    """
    As a listen-accept interface, this function can be
    assigned to web.wsgi.runwsgi.
    """
    if stat.S_ISSOCK(os.fstat(0)[stat.ST_MODE]):
        s_l = socket.fromfd(0, socket.AF_INET, socket.SOCK_STREAM)
        if sys.stderr:
            sys.stderr.close()
        try:
            if len(ERROR_LOG_PATH.strip()) > 0:
                sys.stderr = open(ERROR_LOG_PATH, "a")
            else:
                sys.stderr = None
        except:
            pass
    else:
        s_l = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s_l.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s_l.bind( ("127.0.0.1", SERVER_PORT) )
        s_l.listen(1)

    def writeError(msg):
        if sys.stderr:
            sys.stderr.write(msg.strip() + '\n')

    def writeDetailError(request):
        writeError( time.strftime( '[%Y-%m-%d %H:%M:%S] ', time.localtime() ) )
        writeError(str(request))

    def flushError():
        if sys.stderr:
            sys.stderr.flush()

    while True:
        try:
            s_a = s_l.accept()[0]
        except:
            writeError("Accept failed!")
            break
        finally:
            flushError()

        try:
            request = parseRequest(s_a)
        except Exception, e:
            s_a.close()
            writeError("Parse request failed!")
            writeError(traceback.format_exc())
            continue
        finally:
            flushError()

        def nginx_start_response(status, headers):
            try:
                s_a.send("HTTP/1.1 " + status + "\r\n")
                for (k, v) in headers:
                    s_a.send( "{0}: {1}\r\n".format(k, v) )
                s_a.send("\r\n")
            except:
                if IGNORE_SEND_EXCEPTION:
                    pass
                else:
                    raise

            '''write log start'''
            if FOOT_PRINTS_PATH:
                f_log = open(FOOT_PRINTS_PATH, "a")
            else:
                f_log = None

            def writeKey(k):
                if f_log:
                    f_log.write(' "')
                    if request.has_key(k):
                        f_log.write( quote( str(request[k]) ) )
                    f_log.write('"')

            if f_log:
                f_log.write( time.strftime( '"%Y-%m-%d/%H:%M:%S"',
                    time.localtime() ) )
                f_log.write(' "' + quote(request["REMOTE_ADDR"] +
                    ":" + request["REMOTE_PORT"]) + '"')
                f_log.write(' "' + quote(status.split(" ")[0]) + '"')

            writeKey("REQUEST_METHOD")
            writeKey("REQUEST_URI")
            writeKey("HTTP_REFERER")
            writeKey("HTTP_COOKIE")
            writeKey("HTTP_USER_AGENT")
            writeKey("request_log")

            if f_log:
                f_log.write("\n")
                f_log.close()
            '''write log end'''
            #end nginx_start_response
        
        try:
            if request.has_key('HTTP_COOKIE'):
                request['HTTP_COOKIE'] = justVowels(request['HTTP_COOKIE'])
            #print '======log start=======\n'
            #print  time.strftime( '[%Y-%m-%d %H:%M:%S] ', time.localtime() ) 
            #print str(request)
            #if request.has_key('wsgi.input'):
            #    print str(request['wsgi.input'].getvalue())
            response = func(request, nginx_start_response)
            #print  time.strftime( '[%Y-%m-%d %H:%M:%S] ', time.localtime() ) 
            #print '======log end=======\n'

            try:
                for chunk in response:
                    s_a.send(chunk)
            except:
                if IGNORE_SEND_EXCEPTION:
                    pass
                else:
                    raise

        except:
            s_a.close()
            writeError("Process request failed!")
            writeError(traceback.format_exc())
            continue

        finally:
            flushError()

        s_a.close()

web.wsgi.runwsgi = nginxRunuwsgi