#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

"""proxy server
"""

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import json
import socket
import base64
import random
import httplib
from tornado import web, ioloop, httpclient, iostream

import local

unsupport_headers = ['connection', 'keep-alive', 'proxy-authenticate', 'upgrade'
                     'proxy-authorization', 'te', 'trailers', 'transfer-encoding',
                     '']

class ProxyHandler(web.RequestHandler):
    """handle for proxy request
    """
    SUPPORTED_METHODS = ["GET", "POST", "CONNECT"]

    @web.asynchronous
    def get(self):
        def handle_response(response):
            if response.code not in httplib.responses:
                self.set_status(500, "local server:%s,%s" % (response.code , response.reason))
            else:
                self.set_status(response.code, response.reason)
            for header in response.headers.keys():
                v = response.headers.get(header)
                source = "sae" if response.request.url.rfind("sinaapp.com") != -1 \
                    else "bae"
                print header
                if is_need_header(header, source):
                    print "..", header
                    self.set_header(header, v)

            if response.body:
                self.write(response.body)
            self.finish()


        req = handle_request(self.request)
        client = httpclient.AsyncHTTPClient()
        try:
            client.fetch(req, handle_response)
        except httpclient.HTTPError, e:
            if hasattr(e, "response") and e.response:
                handle_response(e.response)
            else:
                self.set_status(500)
                self.write("local Internal server error:\n" + str(e))
                self.finish()

    @web.asynchronous
    def post(self):
        return self.get()

    @web.asynchronous
    def connect(self):
        host, port = self.request.uri.split(':')
        client = self.request.connection.stream

        def read_from_client(data):
            upstream.write(data)

        def read_from_upstream(data):
            client.write(data)

        def client_close(data=None):
            if upstream.closed():
                return
            if data:
                upstream.write(data)
            upstream.close()

        def upstream_close(data=None):
            if client.closed():
                return
            if data:
                client.write(data)
            client.close()

        def start_tunnel():
            client.read_until_close(client_close, read_from_client)
            upstream.read_until_close(upstream_close, read_from_upstream)
            client.write(b'HTTP/1.0 200 Connection established\r\n\r\n')

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        upstream = iostream.IOStream(s)
        upstream.connect((host, int(port)), start_tunnel)

def build_param_body(req):
    if req.body is not None:
        encode_body = base64.encodestring(req.body)
    else:
        encode_body = req.body

    param_dict = {
        "url": req.uri,
        "method": req.method,
        "headers": req.headers,
        "body": encode_body,
    }
    return json.dumps(param_dict, ensure_ascii=True)

def build_request_for_app(req):
    SINAURL = random.choice(local.urls)
    new_req = httpclient.HTTPRequest(SINAURL, method="POST", body=build_param_body(req),
                                     allow_nonstandard_methods=True, connect_timeout=10,
                                     follow_redirects=False,
                                     request_timeout=12000)
    return new_req

def is_need_header(header_name, proxy_source):
    lower_header_name = header_name.lower()
    if lower_header_name in unsupport_headers:
        return False
    if lower_header_name in ["content-length"]:
        return False
    if proxy_source == "sae":
        if lower_header_name in ["content-encoding"]:
            return False
    return True

def handle_request(req):
    return build_request_for_app(req)

settings = {
    "debug": True
}

def run_proxy(port=2345):
    """run proxy on the specified port
    """

    app = web.Application(
        [(r".*", ProxyHandler)], **settings
    )
    app.listen(port)
    ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    run_proxy(local.port)