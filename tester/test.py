#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@date: 2012-11-14
@author: shell.xu
'''
import sys, gevent, logging
from getopt import getopt
from urlparse import urlparse
from gevent import socket, pool
import http, socks

c = socks.socks5(('localhost', 1081))(socket.socket)
def download(uri):
    url = urlparse(uri)

    r = (url.netloc or url.path).split(':', 1)
    if len(r) > 1: port = int(r[1])
    else: port = 443 if url.scheme.lower() == 'https' else 80
    hostname, port = r[0], port
    uri = url.path + ('?'+url.query if url.query else '')

    req = http.request_http(uri)
    req.set_header("Host", url.hostname)
    res = http.http_client(req, (hostname, port), c)
    res.debug()
    return res.read_body()

def doloop(url, d):
    counter = [0, 0, 0, 0]
    def writest(ch):
        sys.stdout.write(
            '%d/%d/%d/%d = %f/%f/%f%s' % (
                counter[0], counter[1], counter[2], counter[3],
                float(counter[0])/float(counter[3]), float(counter[1])/float(counter[3]),
                float(counter[2])/float(counter[3]), ch))
        
    def tester():
        counter[3] += 1
        try:
            e = download(url)
            if d == e: counter[0] += 1
            else: counter[1] += 1
        except Exception, e: counter[2] += 1
        writest('\r')

    p = pool.Pool(200)
    for i in xrange(2000): p.spawn(tester)
    p.join()
    writest('\n')

def initlog(lv, logfile=None):
    rootlog = logging.getLogger()
    if logfile: handler = logging.FileHandler(logfile)
    else: handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            '%(asctime)s,%(msecs)03d (%(process)d)%(name)s[%(levelname)s]: %(message)s',
            '%H:%M:%S'))
    rootlog.addHandler(handler)
    rootlog.setLevel(lv)

def main():
    initlog(logging.INFO)
    optlist, args = getopt(sys.argv[1:], "o")
    optdict = dict(optlist)
    if not args: url = 'http://localhost/'
    else: url = args[0]
    d = download(url)
    if '-o' in optdict:
        print d
    else: doloop(url, d)

if __name__ == '__main__': main()
