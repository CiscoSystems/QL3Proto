#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2011 Nicira Networks, Inc.
# Copyright 2011 Cisco Systems, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
# @author: Somik Behera, Nicira Networks, Inc.
# @author: Brad Hall, Nicira Networks, Inc.
# @author: Dan Wendlandt, Nicira Networks, Inc.
# @author: Sumit Naiksatam, Cisco Systems, Inc.

import ConfigParser
import logging as LOG
import MySQLdb
import os
import sys
import time
import signal

from optparse import OptionParser
from subprocess import *


class LinuxBridge:
    def __init__(self, br_name_prefix, physical_interface):
        self.br_name_prefix = br_name_prefix
        self.physical_interface = physical_interface

    def run_cmd(self, args):
        LOG.debug("Running command: " + " ".join(args))
        p = Popen(args, stdout=PIPE)
        retval = p.communicate()[0]
        if p.returncode == -(signal.SIGALRM):
            LOG.debug("Timeout running command: " + " ".join(args))
        if retval:
            LOG.debug("Command returned: %s" % retval)
        return retval

    def device_exists(self, device):
        """Check if ethernet device exists."""
        retval = self.run_cmd(['ip', 'link', 'show', 'dev', device])
        if retval:
            return True
        else:
            return False

    def get_brdige_name(self, vlan_id):
        bridge_name = '%s%s' % (self.br_name_prefix, vlan_id)
        return bridge_name

    def get_subinterface_name(self, vlan_id):
        subinterface_name = '%s.%s' % (self.physical_interface, vlan_id)
        return subinterface_name

    def get_tap_device_name(self, interface_id):
        tap_device_name = "tap" + interface_id[0:11]
        return tap_device_name

    def get_tap_devices_for_bridge(self, bridge_name, subinterface):
        if self.device_exists(bridge_name):
            retval = self.run_cmd(['brctl', 'show'])
            rows = retval.split('\n')
            split_rows = {}
            for row in rows:
                split_row = row.split('\t')
                split_rows[split_row[0]] = split_row

            added_interfaces = split_rows[bridge_name][5].split(',')
            added_interfaces.remove(subinterface)
            return added_interfaces

    def get_all_tap_devices(self):
        tap_devices = []
        retval = self.run_cmd(['ip', 'tuntap'])
        rows = retval.split('\n')
        for row in rows:
            split_row = row.split(':')
            if split_row[0].startswith("tap"):
                tap_devices.append(split_row[0])

        return tap_devices

    def get_bridge_for_tap_device(self, tap_device_name):
        retval = self.run_cmd(['brctl', 'show'])
        rows = retval.split('\n')
        split_rows = {}
        for row in rows:
            split_row = row.split('\t')
            added_interfaces = split_row[5].split(',')
            if tap_device_name in added_interfaces:
                return split_row[0]

        return None

    def ensure_vlan_bridge(self, vlan_id):
        """Create a vlan and bridge unless they already exist."""
        interface = self.ensure_vlan(vlan_id)
        bridge_name = self.get_brdige_name(vlan_id)
        self.ensure_bridge(bridge_name, interface)
        return interface

    def ensure_vlan(self, vlan_id):
        """Create a vlan unless it already exists."""
        interface = self.get_subinterface_name(vlan_id)
        if not self.device_exists(interface):
            LOG.debug("Creating subinterface %s for VLAN %s on interface %s" %
                      (interface, vlan_id, self.physical_interface))
            if self.run_cmd(['ip', 'link', 'add', 'link',
                             self.physical_interface,
                             'name', interface, 'type', 'vlan', 'id',
                             vlan_id]):
                return
            if self.run_cmd(['ip', 'link', 'set', interface, 'up']):
                return
            LOG.debug("Done creating subinterface %s" % interface)
        return interface

    def ensure_bridge(self, bridge_name, interface):
        """Create a bridge unless it already exists.

        The code will attempt to move any ips that already exist on the
        interface onto the bridge and reset the default gateway if necessary.
        """
        if not self.device_exists(bridge_name):
            LOG.debug("Starting bridge %s for subinterface %s" % (bridge_name,
                                                                interface))
            if self.run_cmd(['brctl', 'addbr', bridge_name]):
                return
            if self.run_cmd(['brctl', 'setfd', bridge_name, str(0)]):
                return
            if self.run_cmd(['brctl', 'stp', bridge_name, 'off']):
                return
            if self.run_cmd(['ip', 'link', 'set', bridge_name, 'up']):
                return
            if self.run_cmd(['brctl', 'addif', bridge_name, interface]):
                return
            LOG.debug("Done starting bridge %s for subinterface %s" %
                      (bridge_name, interface))


    def add_tap_interface(self, vlan_id, interface_id):
        tap_device_name = self.get_tap_device_name(interface_id)
        if not self.device_exists(tap_device_name):
            LOG.debug("Tap device: %s does not exist on this host, skipped" %
                      tap_device_name) 
            return

        if interface_id:
            LOG.debug("Adding device %s to bridge %s" % (tap_device_name,
                                                         bridge_name))
            current_bridge_name = \
                    self.get_bridge_for_tap_device(tap_device_name)
            if current_bridge_name:
                if self.run_cmd(['brctl', 'delif', current_bridge_name,
                                 tap_device_name]):
                    return

            self.ensure_vlan_brdige(vlan_id)
            if self.run_cmd(['brctl', 'addif', bridge_name, tap_device_name]):
                return
            LOG.debug("Done adding device %s to bridge %s" % (tap_device_name,
                                                              bridge_name))

    def remove_interfaces(self, added_interfaces):
        for tap_device in self.get_all_tap_devices():
            if tap_device not in added_interfaces:
                current_bridge_name = \
                        self.get_bridge_for_tap_device(tap_device)
                LOG.debug("Removing device %s from bridge %s" % \
                          (tap_device, current_bridge_name))
                if current_bridge_name:
                    if self.run_cmd(['brctl', 'delif', current_bridge_name,
                                     tap_device]):
                    return
                LOG.debug("Done removing device %s from bridge %s" % \
                          (tap_device, current_bridge_name))


    def delete_bridge(self, vlan_id):
        bridge_name = self.get_brdige_name(vlan_id)
        if self.device_exists(bridge_name):
            interface = self.get_subinterface_name(vlan_id)
            LOG.debug("Deleting bridge %s" % bridge_name)
            if self.run_cmd(['brctl', 'delif', bridge_name, interface]):
                return
            if self.run_cmd(['ip', 'link', 'set', bridge_name, 'down']):
                return
            if self.run_cmd(['brctl', 'delbr', bridge_name]):
                return
            LOG.debug("Done deleting bridge %s" % bridge_name)

    def delete_subinterface(self, vlan_id):
        interface = self.get_subinterface_name(vlan_id)
        if self.device_exists(interface):
            LOG.debug("Deleting subinterface %s" % interface)
            if self.run_cmd(['ip', 'link', 'set', interface, 'down']):
                return
            if self.run_cmd(['ip', 'link', 'delete', interface]):
                return
            LOG.debug("Done deleting subinterface %s" % interface)

    def delete_subinterface_bridge(self, vlan_id):
        bridge_name = self.get_brdige_name(vlan_id)
        subinterface = self.get_subinterface_name(vlan_id)
        if self.device_exists(bridge_name) and \
           not self.get_tap_devices_for_bridge(bridge_name, subinterface):
            self.delete_bridge(vlan_id)
            self.delete_subinterface(vlan_id)
        return

class LinuxBridgeQuantumAgent:

    def __init__(self, br_name_prefix, physical_interface, polling_interval):
        self.polling_interval = int(polling_interval)
        self.setup_linux_bridge(br_name_prefix, physical_interface)

    def setup_linux_bridge(self, br_name_prefix, physical_interface):
        self.linux_br = LinuxBridge(br_name_prefix, physical_interface)

    def process_port_binding(self, port_id, network_id, interface_id,
                             vlan_id):
        self.linux_br.add_tap_interface(vlan_id, interface_id)

    def process_vlan_binding(self, network_id, vlan_id):
        self.linux_br.delete_subinterface_bridge(vlan_id)

    def daemon_loop(self, conn):
        self.added_interfaces = []

        while True:
            cursor = MySQLdb.cursors.DictCursor(conn)
            cursor.execute("SELECT * FROM vlan_bindings")
            rows = cursor.fetchall()
            cursor.close()
            vlan_bindings = {}
            vlans_string = ""
            for r in rows:
                vlan_bindings[r['network_id']] = r
                vlans_string = "%s %s" % (vlans_string, r)
                #self.linux_br.ensure_vlan_bridge(str(r['vlan_id']))

            LOG.debug("VLAN-bindings: %s" % vlans_string) 

            cursor = MySQLdb.cursors.DictCursor(conn)
            cursor.execute("SELECT * FROM ports where state = 'ACTIVE'")
            rows = cursor.fetchall()
            cursor.close()
            port_bindings = {}
            ports_string = ""
            for r in rows:
                ports_string = "%s %s" % (ports_string, r)
                vlan_id = str(vlan_bindings[r['network_id']]['vlan_id'])
                self.process_port_binding(r['uuid'], r['network_id'],
                                          r['interface_id'], vlan_id)
                if r['interface_id']:
                    self.added_interfaces.append(r['interface_id'])
            LOG.debug("Port-bindings: %s" % ports_string) 

            self.linux_br.remove_interfaces(self.added_interfaces)
            
            for binding in vlan_bindings:
                self.process_vlan_binding(vlan_bindings[binding],
                                          str(vlan_bindings[binding]\
                                              ['vlan_id']))
            conn.commit()
            time.sleep(self.polling_interval)

if __name__ == "__main__":
    usagestr = "%prog [OPTIONS] <config file>"
    parser = OptionParser(usage=usagestr)
    parser.add_option("-v", "--verbose", dest="verbose",
      action="store_true", default=False, help="turn on verbose logging")

    options, args = parser.parse_args()

    if options.verbose:
        LOG.basicConfig(level=LOG.DEBUG)
    else:
        LOG.basicConfig(level=LOG.WARN)

    if len(args) != 1:
        parser.print_help()
        sys.exit(1)

    config_file = args[0]
    config = ConfigParser.ConfigParser()
    try:
        fh = open(config_file)
        fh.close()
        config.read(config_file)
        br_name_prefix = config.get("LINUX_BRIDGE", "bridge_name")
        physical_interface = config.get("LINUX_BRIDGE", "physical_interface")
        polling_interval = config.get("AGENT", "polling_interval")
        db_name = config.get("DATABASE", "name")
        db_user = config.get("DATABASE", "user")
        db_pass = config.get("DATABASE", "pass")
        db_host = config.get("DATABASE", "host")
    except Exception, e:
        LOG.error("Unable to parse config file \"%s\": \nException%s"
                  % (config_file, str(e)))
        sys.exit(1)

    conn = None
    try:
        LOG.info("Connecting to database \"%s\" on %s" % (db_name, db_host))
        conn = MySQLdb.connect(host=db_host, user=db_user,
          passwd=db_pass, db=db_name)
        plugin = LinuxBridgeQuantumAgent(br_name_prefix, physical_interface,
                                         polling_interval)
        plugin.daemon_loop(conn)
    finally:
        if conn:
            conn.close()

    sys.exit(0)
