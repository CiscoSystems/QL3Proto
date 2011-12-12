# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2011, Cisco Systems, Inc.
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
# @author: Sumit Naiksatam, Cisco Systems, Inc.

import logging

from quantum.common import exceptions as exc
from quantum.plugins.linuxbridge import plugin_configuration as conf
from quantum.plugins.linuxbridge.common import constants as const
from quantum.plugins.linuxbridge.common import utils as cutil
from quantum.plugins.linuxbridge.db import api as db
from quantum.plugins.linuxbridge.db import l2network_db as cdb

LOG = logging.getLogger('quantum.plugins.linuxbridge.LinuxBridgePlugin')


class LinuxBridgePlugin(object):
    """
    LinuxBridgePlugin provides support for Quantum abstractions
    using LinuxBridge. A new VLAN is created for each network.
    It relies on an agent to perform the actual bridge configuration
    on each host.
    """

    def __init__(self):
        #db.configure_db({'sql_connection': 'sqlite:///:memory:'})
        cdb.initialize()
        cdb.create_vlanids()
        LinuxBridgePlugin._net_counter = 0

    def _get_vlan_for_tenant(self, tenant_id, net_name, **kwargs):
        """Get an available VLAN ID"""
        return cdb.reserve_vlanid()

    def _release_vlan_for_tenant(self, tenant_id, net_id, **kwargs):
        """Release the ID"""
        vlan_binding = cdb.get_vlan_binding(net_id)
        return cdb.release_vlanid(vlan_binding[const.VLANID])

    def _get_vlan_name(self, net_id, vlan):
        """Getting the vlan name from the tenant and vlan"""
        vlan_name = conf.VLAN_NAME_PREFIX + vlan
        return vlan_name

    def _validate_port_state(self, port_state):
        if port_state.upper() not in ('ACTIVE', 'DOWN'):
            raise exc.StateInvalid(port_state=port_state)
        return True

    def get_all_networks(self, tenant_id):
        """
        Returns a dictionary containing all
        <network_uuid, network_name> for
        the specified tenant.
        """
        LOG.debug("LinuxBridgePlugin.get_all_networks() called")
        networks_list = db.network_list(tenant_id)
        new_networks_list = []
        for network in networks_list:
            new_network_dict = cutil.make_net_dict(network[const.UUID],
                                                   network[const.NETWORKNAME],
                                                   [])
            new_networks_list.append(new_network_dict)

        return new_networks_list

    def get_network_details(self, tenant_id, net_id):
        """
        retrieved a list of all the remote vifs that
        are attached to the network
        """
        LOG.debug("LinuxBridgePlugin.get_network_details() called")
        network = db.network_get(net_id)
        ports_list = network[const.NETWORKPORTS]
        ports_on_net = []
        for port in ports_list:
            new_port = cutil.make_port_dict(port[const.UUID],
                                            port[const.PORTSTATE],
                                            port[const.NETWORKID],
                                            port[const.INTERFACEID])
            ports_on_net.append(new_port)

        new_network = cutil.make_net_dict(network[const.UUID],
                                              network[const.NETWORKNAME],
                                              ports_on_net)

        return new_network

    def create_network(self, tenant_id, net_name, **kwargs):
        """
        Creates a new Virtual Network, and assigns it
        a symbolic name.
        """
        LOG.debug("LinuxBridgePlugin.create_network() called")
        new_network = db.network_create(tenant_id, net_name)
        new_net_id = new_network[const.UUID]
        vlan_id = self._get_vlan_for_tenant(tenant_id, net_name)
        vlan_name = self._get_vlan_name(new_net_id, str(vlan_id))
        cdb.add_vlan_binding(vlan_id, vlan_name, new_net_id)
        new_net_dict = {const.NET_ID: new_net_id,
                        const.NET_NAME: net_name,
                        const.NET_PORTS: []}
        return new_net_dict

    def delete_network(self, tenant_id, net_id):
        """
        Deletes the network with the specified network identifier
        belonging to the specified tenant.
        """
        LOG.debug("LinuxBridgePlugin.delete_network() called")
        net = db.network_get(net_id)
        if net:
            if len(net[const.NETWORKPORTS]) > 0:
                ports_on_net = db.port_list(net_id)
                for port in ports_on_net:
                    if port[const.INTERFACEID]:
                        raise exc.NetworkInUse(net_id=net_id)
                for port in ports_on_net:
                    self.delete_port(tenant_id, net_id, port[const.UUID])

            net_dict = cutil.make_net_dict(net[const.UUID],
                                           net[const.NETWORKNAME],
                                           [])
            self._release_vlan_for_tenant(tenant_id, net_id)
            cdb.remove_vlan_binding(net_id)
            db.network_destroy(net_id)
            return net_dict
        # Network not found
        raise exc.NetworkNotFound(net_id=net_id)

    def update_network(self, tenant_id, net_id, **kwargs):
        """
        Updates the attributes of a particular Virtual Network.
        """
        LOG.debug("LinuxBridgePlugin.update_network() called")
        network = db.network_update(net_id, tenant_id, **kwargs)
        net_dict = cutil.make_net_dict(network[const.UUID],
                                       network[const.NETWORKNAME],
                                       [])
        return net_dict

    def get_all_ports(self, tenant_id, net_id):
        """
        Retrieves all port identifiers belonging to the
        specified Virtual Network.
        """
        LOG.debug("LinuxBridgePlugin.get_all_ports() called")
        network = db.network_get(net_id)
        ports_list = network[const.NETWORKPORTS]
        ports_on_net = []
        for port in ports_list:
            new_port = cutil.make_port_dict(port[const.UUID],
                                            port[const.PORTSTATE],
                                            port[const.NETWORKID],
                                            port[const.INTERFACEID])
            ports_on_net.append(new_port)

        return ports_on_net

    def get_port_details(self, tenant_id, net_id, port_id):
        """
        This method allows the user to retrieve a remote interface
        that is attached to this particular port.
        """
        LOG.debug("LinuxBridgePlugin.get_port_details() called")
        network = db.network_get(net_id)
        port = db.port_get(net_id, port_id)
        new_port_dict = cutil.make_port_dict(port[const.UUID],
                                             port[const.PORTSTATE],
                                             port[const.NETWORKID],
                                             port[const.INTERFACEID])
        return new_port_dict

    def create_port(self, tenant_id, net_id, port_state=None, **kwargs):
        """
        Creates a port on the specified Virtual Network.
        """
        LOG.debug("LinuxBridgePlugin.create_port() called")
        port = db.port_create(net_id, port_state)
        unique_port_id_string = port[const.UUID]
        new_port_dict = cutil.make_port_dict(port[const.UUID],
                                             port[const.PORTSTATE],
                                             port[const.NETWORKID],
                                             port[const.INTERFACEID])
        return new_port_dict

    def update_port(self, tenant_id, net_id, port_id, **kwargs):
        """
        Updates the attributes of a port on the specified Virtual Network.
        """
        LOG.debug("LinuxBridgePlugin.update_port() called")
        network = db.network_get(net_id)
        self._validate_port_state(kwargs["state"])
        db.port_update(port_id, net_id, **kwargs)

        new_port_dict = cutil.make_port_dict(port_id, kwargs["state"], net_id,
                                             None)
        return new_port_dict

    def delete_port(self, tenant_id, net_id, port_id):
        """
        Deletes a port on a specified Virtual Network,
        if the port contains a remote interface attachment,
        the remote interface is first un-plugged and then the port
        is deleted.
        """
        LOG.debug("LinuxBridgePlugin.delete_port() called")
        network = db.network_get(net_id)
        port = db.port_get(net_id, port_id)
        attachment_id = port[const.INTERFACEID]
        if not attachment_id:
            db.port_destroy(net_id, port_id)
            new_port_dict = cutil.make_port_dict(port_id, None, None, None)
            return new_port_dict
        else:
            raise exc.PortInUse(port_id=port_id, net_id=net_id,
                                att_id=attachment_id)

    def plug_interface(self, tenant_id, net_id, port_id, remote_interface_id):
        """
        Attaches a remote interface to the specified port on the
        specified Virtual Network.
        """
        LOG.debug("LinuxBridgePlugin.plug_interface() called")
        network = db.network_get(net_id)
        port = db.port_get(net_id, port_id)
        attachment_id = port[const.INTERFACEID]
        if attachment_id:
            raise exc.PortInUse(port_id=port_id, net_id=net_id,
                                att_id=attachment_id)
        db.port_set_attachment(net_id, port_id, remote_interface_id)

    def unplug_interface(self, tenant_id, net_id, port_id):
        """
        Detaches a remote interface from the specified port on the
        specified Virtual Network.
        """
        LOG.debug("LinuxBridgePlugin.unplug_interface() called")
        network = db.network_get(net_id)
        port = db.port_get(net_id, port_id)
        attachment_id = port[const.INTERFACEID]
        if attachment_id == None:
            raise exc.InvalidDetach(port_id=port_id, net_id=net_id,
                                    att_id=remote_interface_id)
        db.port_unset_attachment(net_id, port_id)
