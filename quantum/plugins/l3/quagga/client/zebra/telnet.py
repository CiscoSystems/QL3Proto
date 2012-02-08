import iplib
import re
import sys
import telnetlib
import logging

from quantum.common import exceptions as exc

LOG = logging.getLogger('quantum.plugins.QuaggaClient')


class QuaggaClient(object):
    def __init__(self, password, en_password, host="localhost", port="2601"):
        self.host = host
        self.port = port
        self.password = password
        self.en_password = en_password

        self._login()


    def __del__(self):
        self._logout()


    def _login(self):
        
        try:
            self.conn = telnetlib.Telnet(self.host, self.port)
            self.conn.read_until("Password: ")
            self.conn.write(self.password + "\n")
            self.conn.write("en\n")
            self.conn.read_until("Password: ")
            self.conn.write(self.en_password + "\n")
        except:
            raise exc.ServiceContactError(service="Quagga")


    def _logout(self):
        self.conn.close()


    def add_static_route(self, destination, netmask, next_hop):
        self.conn.write("conf t\n")
        cmd = "ip route %s %s %s\n" % (destination, netmask, next_hop)
        LOG.debug("Running command '%s'" % cmd)
        self.conn.write(cmd.encode('ascii', 'ignore'))
        self.conn.write("exit\n")
        self.conn.write("en\n")

        outp = self.conn.read_until("# en")

        if re.search("Unknown command", outp):
            raise exc.InvalidCommandError(command=cmd)
        else:
            return True

    def del_static_route(self, destination, netmask, next_hop):
        self.conn.write("conf t\n")
        cmd = "no ip route %s %s %s\n" % (destination, netmask, next_hop)
        self.conn.write(cmd.encode('ascii', 'ignore'))
        self.conn.write("exit\n")
        self.conn.write("en\n")

        outp = self.conn.read_until("# en")

        if re.search("Unknown command", outp):
            raise exc.InvalidCommandError(command=cmd)
        else:
            return True


    def get_all_routes(self):
        self.conn.write("sh ip route\n")
        self.conn.write("en\n")

        outp = self.conn.read_until("# en")
 
        route_table = []

        for line in outp.split("\n"):
            if re.search(r"[A-Z]>\*\s+[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\/[0-9]+",
                         line):
                m = re.search(
                      "([A-Z])>\*?\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\/([0-9]+)",
                      line)
                if m.group(2) == '127.0.0.0':
                    continue
                dest = m.group(2)
                mask = m.group(3)
                rtype = m.group(1)
                target = 'direct'
                interface = ''

                if re.search(r"via\s+[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+", line):
                    t = re.search(
                         r"via\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+),\s+(\w+)\W*$",
                         line)
                    target = t.group(1)
                    interface = t.group(2)
                else:
                    t = re.search(r"is directly connected,\s+(\w+)\W*$", line)
                    interface = t.group(1)

                route_table.append((dest, mask, target, rtype, interface))

        return route_table


    def get_subnet_target(self, destination, netmask):
        bits = iplib.convert_nm(netmask, notation='bits')
        self.conn.write("sh ip route %s/%s\n" % (destination, bits))
        self.conn.write("en\n")

        outp = self.conn.read_until("# en")

        target = None
        for line in outp.split("\n"):
            if re.search(r"\*\s+[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+", line):
                m = re.search(
                      r"\*\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)",
                      line)
                target = m.group(1)
            elif re.search(r"\* directly connected", line):
                target = 'direct'

        return target


    def update_static_route(self, destination, netmask, next_hop):
        self.add_static_route(destination, netmask, next_hop)
