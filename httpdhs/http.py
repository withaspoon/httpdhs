import cherrypy
import urllib
import urllib2
from node import NodeDownError
from cherrypy import request
from cherrypy import dispatch

class HttpServer(object):
    def __init__(self, backend):
        self._backend = backend
    
    def run(self, port, max_threads):
        root = ServerHandler(self._backend)
        dispatcher = cherrypy.dispatch.RoutesDispatcher()
        dispatcher.connect('create', '/db/{key}', controller=root.db, action='create', conditions=dict(method=['PUT']))
        dispatcher.connect('read', '/db/{key}', controller=root.db, action='read', conditions=dict(method=['GET']))
        cherrypy.quickstart(root, '/', {
            'global': { 'server.socket_port': port, 'server.thread_pool': max_threads },
            '/db': { 'request.dispatch': dispatcher }
        })

class DatabaseHandler(object):
    def __init__(self, backend):
        self._backend = backend
    
    exposed = True
    
    def read(self, key):
        value = self._backend.get(key)
        if value:
            return "%s=%s" % (key, value)
        else:
            return 'not_found'
    
    def create(self, key, value, direct='false'):
        if direct == 'true':
            self._backend.set_direct(key, value)
        else:
            self._backend.set(key, value)
        return "%s=%s" % (key, value)
        

class ServerHandler(object):
    def __init__(self, backend):
        self.db = DatabaseHandler(backend)

class HttpClient(object):
    def get(self, address, key):
        result = self._http_get(address, key)
        if result != "not_found":
            return result.split("=")[1]

    def set_without_replication(self, address, key, value):
        self._http_post(address, key, {'value': value, 'direct': 'true'})

    def set(self, address, key, value):
        self._http_post(address, key, {'value': value})

    def _http_get(self, address, key):
        try:
            return urllib2.urlopen("http://%s/db/%s" % (address, key)).read()
        except urllib2.URLError:
            raise NodeDownError()

    def _http_post(self, address, key, params):
        try:
            data = self._utf8_query_string_from_dict(params)
            request = urllib2.Request("http://%s/db/%s" % (address, key), data)
            request.get_method = lambda: 'PUT'
            response = urllib2.urlopen(request)
            return response.read()
        except urllib2.URLError:
            raise NodeDownError()

    def _utf8_query_string_from_dict(self, params):
        return urllib.urlencode(dict([k, v.encode('utf-8')] for k, v in params.items()))