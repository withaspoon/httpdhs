import cherrypy
import urllib
import urllib2
from node import NodeDownError
from cherrypy import request
from cherrypy import dispatch

class HttpServer(object):
    """Entry class for the http server interface.
    
    Sets up routes and configures the web server for database access. After
    calling run the method never returns."""
    
    def __init__(self, controller):
        self._controller = controller
    
    def run(self, port, max_threads, env):
        root = ServerHandler(self._controller)
        dispatcher = self._create_dispatcher(root)
        cherrypy.quickstart(root, '/', {
            'global': {
                'server.socket_port': port,
                'server.thread_pool': max_threads,
                'environment': env
            },
            '/db': { 'request.dispatch': dispatcher }
        })
    
    def _create_dispatcher(self, root):
        dispatcher = cherrypy.dispatch.RoutesDispatcher()
        dispatcher.connect('create', '/db/{key}', controller=root.db, action='update', conditions=dict(method=['PUT']))
        dispatcher.connect('read', '/db/{key}', controller=root.db, action='read', conditions=dict(method=['GET']))
        return dispatcher

class DatabaseHandler(object):
    """Cherrypy handler for database access"""
    
    exposed = True
    
    def __init__(self, controller):
        self._controller = controller
    
    def read(self, key):
        value = self._controller.get(key)
        if value:
            return "%s=%s" % (key, value)
        else:
            raise cherrypy.HTTPError(404)
    
    def update(self, key, value, direct='false'):
        if direct == 'true':
            self._controller.set_direct(key, value)
        else:
            self._controller.set(key, value)
        return "%s=%s" % (key, value)
        

class ServerHandler(object):
    """Root cherrypy handler"""
    
    def __init__(self, controller):
        self.db = DatabaseHandler(controller)

class HttpClient(object):
    """HTTP Client for querying the key value database using REST.
    
    set_without_replication is used internally for updating a key without
    causing an infinite loop of requests."""
    
    def get(self, address, key):
        result = self._http_get(address, key)
        if "=" in result:
            return result.split("=")[1]

    def set_without_replication(self, address, key, value):
        self._http_put(address, key, {'value': value, 'direct': 'true'})

    def set(self, address, key, value):
        self._http_put(address, key, {'value': value})

    def _http_get(self, address, key):
        try:
            return urllib2.urlopen("http://%s/db/%s" % (address, key)).read()
        except urllib2.URLError:
            raise NodeDownError()

    def _http_put(self, address, key, params):
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
