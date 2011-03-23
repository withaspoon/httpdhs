import cherrypy
from cherrypy import request

class Server(object):
    def __init__(self, backend):
        self._backend = backend
    
    def run(self, port):
        cherrypy.config.update({'server.socket_port': int(port)})
        cherrypy.quickstart(ServerHandler(self._backend), '/', {})

class DatabaseHandler(object):
    def __init__(self, backend):
        self._backend = backend
    
    @cherrypy.expose
    def get(self, key):
        value = self._backend.get(key)
        if value:
            return "%s=%s" % (key, value)
        else:
            return "not_found"
    
    @cherrypy.expose
    def set(self, key, value):
        self._backend.set(key, value)
        return "%s=%s" % (key, value)
    
    @cherrypy.expose
    def set_direct(self, key, value):
        self._backend.set_direct(key, value)

class ServerHandler(object):
    def __init__(self, backend):
        self.db = DatabaseHandler(backend)
