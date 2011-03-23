from httpdhs.http import HttpServer
from httpdhs.partitioning import ConsistentHashingPartitioningStrategy
from httpdhs.backend import KeyValueController
from optparse import OptionParser

class CliController(object):
    def run(self):
        options = self._parse_options()
        addresses = self._read_addresses_from_config_file(options.conf)

        print "Starting server on port %s in cluster %s" % (options.port, addresses)

        strategy = ConsistentHashingPartitioningStrategy(addresses, int(options.replicas))
        node_name = "localhost:%s" % (options.port)
        controller = KeyValueController(node_name, strategy)
        env = self._environment_string(options.production)
        HttpServer(controller).run(int(options.port), int(options.threads), env)

        print "Done."
    
    def _parse_options(self):
        parser = OptionParser()
        parser.add_option("-p", "--port", dest="port", help="run on port PORT", metavar="PORT")
        parser.add_option("-c", "--conf", dest="conf", help="configuration file for the cluster")
        parser.add_option("-r", "--replicas", dest="replicas", help="number of replicas", default=2)
        parser.add_option("-t", "--threads", dest="threads", help="maximum number of threads", default=50)
        parser.add_option("-P", "--production", action="store_true", dest="production", help="run in production environment")
        (options, args) = parser.parse_args()
        return options
    
    def _read_addresses_from_config_file(self, path):
        config_file = open(path)
        return [address.strip("\n") for address in config_file.readlines()]
    
    def _environment_string(self, production):
        if production:
            return 'production'
    