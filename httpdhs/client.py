import urllib
import urllib2
from node import NodeDownError

class Client(object):
    def get(self, address, key):
        result = self._query(address, "get", {'key': key})
        if result != "not_found":
            return result.split("=")[1]
    
    def set_without_replication(self, address, key, value):
        self._query(address, 'set_direct', {'key': key, 'value': value})
    
    def set(self, address, key, value):
        self._query(address, 'set', {'key': key, 'value': value})
    
    def _query(self, address, action, params):
        try:
            query_string = urllib.urlencode(dict([k, v.encode('utf-8')] for k, v in params.items()))
            return urllib2.urlopen("http://%s/db/%s?%s" % (address, action, query_string)).read()
        except urllib2.URLError:
            raise NodeDownError()