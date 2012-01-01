# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2011 Nicira Networks, Inc.
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

import ConfigParser
import logging as LOG
from optparse import OptionParser
import os
import sys

from quantum.api.api_common import OperationalStatus
from quantum.common import exceptions as q_exc
from quantum.common.config import find_config_file
from quantum.quantum_plugin_base import QuantumPluginBase

import quantum.db.api as db
import ovs_db

CONF_FILE = find_config_file(
  {"config_file": "etc/quantum/plugins/openvswitch/ovs_quantum_plugin.ini"},
  None, "ovs_quantum_plugin.ini")

LOG.basicConfig(level=LOG.WARN)
LOG.getLogger("ovs_quantum_plugin")


class VlanMap(object):
    vlans = {}

    def __init__(self):
        for x in xrange(2, 4094):
            self.vlans[x] = None

    def set(self, vlan_id, network_id):
        self.vlans[vlan_id] = network_id

    def acquire(self, network_id):
        for x in xrange(2, 4094):
            if self.vlans[x] == None:
                self.vlans[x] = network_id
                # LOG.debug("VlanMap::acquire %s -> %s" % (x, network_id))
                return x
        raise Exception("No free vlans..")

    def get(self, vlan_id):
        return self.vlans[vlan_id]

    def release(self, network_id):
        for x in self.vlans.keys():
            if self.vlans[x] == network_id:
                self.vlans[x] = None
                # LOG.debug("VlanMap::release %s" % (x))
                return
        LOG.error("No vlan found with network \"%s\"" % network_id)


class OVSQuantumPlugin(QuantumPluginBase):

    def __init__(self, configfile=None):
        config = ConfigParser.ConfigParser()
        if configfile == None:
            if os.path.exists(CONF_FILE):
                configfile = CONF_FILE
            else:
                configfile = find_config(os.path.abspath(
                        os.path.dirname(__file__)))
        if configfile == None:
            raise Exception("Configuration file \"%s\" doesn't exist" %
              (configfile))
        LOG.debug("Using configuration file: %s" % configfile)
        config.read(configfile)
        LOG.debug("Config: %s" % config)

        options = {"sql_connection": config.get("DATABASE", "sql_connection")}
        db.configure_db(options)

        self.vmap = VlanMap()
        # Populate the map with anything that is already present in the
        # database
        vlans = ovs_db.get_vlans()
        for x in vlans:
            vlan_id, network_id = x
            # LOG.debug("Adding already populated vlan %s -> %s"
            #                                   % (vlan_id, network_id))
            self.vmap.set(vlan_id, network_id)

    def get_all_networks(self, tenant_id):
        nets = []
        for x in db.network_list(tenant_id):
            LOG.debug("Adding network: %s" % x.uuid)
            nets.append(self._make_net_dict(str(x.uuid), x.name,
                                            None, x.op_status))
        return nets

    def _make_net_dict(self, net_id, net_name, ports, op_status):
        res = {'net-id': net_id,
                'net-name': net_name,
                'net-op-status': op_status}
        if ports:
            res['net-ports'] = ports
        return res

    def create_network(self, tenant_id, net_name, **kwargs):
        net = db.network_create(tenant_id, net_name,
                          op_status=OperationalStatus.UP)
        LOG.debug("Created network: %s" % net)
        vlan_id = self.vmap.acquire(str(net.uuid))
        ovs_db.add_vlan_binding(vlan_id, str(net.uuid))
        return self._make_net_dict(str(net.uuid), net.name, [],
                                        net.op_status)

    def delete_network(self, tenant_id, net_id):
        net = db.network_get(net_id)

        # Verify that no attachments are plugged into the network
        for port in db.port_list(net_id):
            if port.interface_id:
                raise q_exc.NetworkInUse(net_id=net_id)
        net = db.network_destroy(net_id)
        ovs_db.remove_vlan_binding(net_id)
        self.vmap.release(net_id)
        return self._make_net_dict(str(net.uuid), net.name, [],
                                        net.op_status)

    def get_network_details(self, tenant_id, net_id):
        net = db.network_get(net_id)
        ports = self.get_all_ports(tenant_id, net_id)
        return self._make_net_dict(str(net.uuid), net.name,
                                    ports, net.op_status)

    def update_network(self, tenant_id, net_id, **kwargs):
        net = db.network_update(net_id, tenant_id, **kwargs)
        return self._make_net_dict(str(net.uuid), net.name,
                                        None, net.op_status)

    def _make_port_dict(self, port):
        if port.state == "ACTIVE":
            op_status = port.op_status
        else:
            op_status = OperationalStatus.DOWN

        return {'port-id': str(port.uuid),
                'port-state': port.state,
                'port-op-status': op_status,
                'net-id': port.network_id,
                'attachment': port.interface_id}

    def get_all_ports(self, tenant_id, net_id):
        ids = []
        ports = db.port_list(net_id)
        return [{'port-id': str(p.uuid)} for p in ports]

    def create_port(self, tenant_id, net_id, port_state=None, **kwargs):
        LOG.debug("Creating port with network_id: %s" % net_id)
        port = db.port_create(net_id, port_state,
                                op_status=OperationalStatus.DOWN)
        return self._make_port_dict(port)

    def delete_port(self, tenant_id, net_id, port_id):
        port = db.port_destroy(port_id, net_id)
        return self._make_port_dict(port)

    def update_port(self, tenant_id, net_id, port_id, **kwargs):
        """
        Updates the state of a port on the specified Virtual Network.
        """
        LOG.debug("update_port() called\n")
        port = db.port_get(port_id, net_id)
        db.port_update(port_id, net_id, **kwargs)
        return self._make_port_dict(port)

    def get_port_details(self, tenant_id, net_id, port_id):
        port = db.port_get(port_id, net_id)
        return self._make_port_dict(port)

    def plug_interface(self, tenant_id, net_id, port_id, remote_iface_id):
        db.port_set_attachment(port_id, net_id, remote_iface_id)

    def unplug_interface(self, tenant_id, net_id, port_id):
        db.port_set_attachment(port_id, net_id, "")
        db.port_update(port_id, net_id, op_status=OperationalStatus.DOWN)

    def get_interface_details(self, tenant_id, net_id, port_id):
        res = db.port_get(port_id, net_id)
        return res.interface_id
