# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2011 Cisco Systems, Inc.
# All Rights Reserved.
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
#
# Extends the linux_net.py kvm/linux network driver in Nova,
# borrows structure and code
# @author: Sumit Naiksatam, Cisco Systems, Inc.
#


"""Extends the linux_net driver when using the Linux Bridge plugin with
QuantumManager"""


import time
from threading import Thread

from nova import exception
from nova import log as logging
from nova import utils

from nova.network.linux_net import *


LOG = logging.getLogger("nova.network.quantum.linux_net_linux_bridge")


INITIALIZE_GATEWAY_SLEEP = 3
MAX_SLEEP_ITERATIONS = 100
BRDIGE_NAME_PREFIX = "brq-"
GATEWAY_INTERFACE_PREFIX = "gw-"
DEVICE_NAME_PLACEHOLDER = "device_name"
DEVICE_FS = "/sys/devices/virtual/net/"
DEVICE_ADDRESS_FS = DEVICE_FS + DEVICE_NAME_PLACEHOLDER + "/address"
BRIDGE_NAME_PLACEHOLDER = "bridge_name"
BRIDGE_INTERFACES_FS = DEVICE_FS + BRIDGE_NAME_PLACEHOLDER + "/brif/"


def _execute(*cmd, **kwargs):
    """Wrapper around utils._execute for fake_network."""
    if FLAGS.fake_network:
        LOG.debug('FAKE NET: %s', ' '.join(map(str, cmd)))
        return 'fake', 0
    else:
        return utils.execute(*cmd, **kwargs)


def _device_exists(device):
    """Check if ethernet device exists."""
    (_out, err) = _execute('ip', 'link', 'show', 'dev', device,
                           check_exit_code=False)
    return not err


def _get_interfaces_on_bridge(bridge_name):
    if _device_exists(bridge_name):
        bridge_interface_path = \
                BRIDGE_INTERFACES_FS.replace(BRIDGE_NAME_PLACEHOLDER,
                                             bridge_name)
        return os.listdir(bridge_interface_path)


def _get_device_mac_address(device_name):
    device_address_path = DEVICE_ADDRESS_FS.replace(DEVICE_NAME_PLACEHOLDER,
                                                    device_name)
    mac_address, err = _execute('cat', device_address_path, run_as_root=True)
    return mac_address


def _get_enslaved_vlan_device_name(bridge_name):
    bridge_mac_address = _get_device_mac_address(bridge_name)
    device_names = _get_interfaces_on_bridge(bridge_name)
    for device_name in device_names:
        device_mac_address = _get_device_mac_address(device_name)
        if device_mac_address == bridge_mac_address:
            return device_name


def _initialize_gateway_device(dev, network_ref):
    if not network_ref:
        LOG.error("Cannot initialize gateway: network_ref is null")
        return

    bridge = BRDIGE_NAME_PREFIX + str(network_ref['uuid'][0:11])
    sleep_counter = MAX_SLEEP_ITERATIONS
    while not _device_exists(bridge) and sleep_counter:
        LOG.debug("Bridge %s does not exist, waiting to initialize gateway",
                  bridge)
        time.sleep(INITIALIZE_GATEWAY_SLEEP)
        sleep_counter = sleep_counter - 1

    if not _device_exists(bridge):
        LOG.error("Cannot initialize gateway: bridge %s does not exist" \
                  % bridge)
        return

    full_ip = '%s/%s' % (network_ref['dhcp_server'],
                         network_ref['cidr'].rpartition('/')[2])
    new_ip_params = [[full_ip, 'brd', network_ref['broadcast']]]
    old_ip_params = []
    """
    We cannot use the originally desingated tap device as the gateway since
    no userspace process/gateway entity connects to the tap device, and
    hence it will not repond on it's IP.
    Instead we will assign the gateway IP to the bridge.
    We will now swap the MAC address on the original gateway device with
    that on the bridge, so that the bridge has the designated gateway
    MAC address
    """
    bridge_mac_address = _get_device_mac_address(bridge)
    gw_mac_address = _get_device_mac_address(dev)
    enslaved_device = _get_enslaved_vlan_device_name(bridge)

    _execute('ip', 'link', 'set', 'dev', enslaved_device, 'down',
             run_as_root=True)
    _execute('ip', 'link', 'set', 'dev', bridge, 'down', run_as_root=True)
    _execute('ip', 'link', 'set', 'dev', dev, 'down', run_as_root=True)

    _execute('ip', 'link', 'set', 'dev', enslaved_device, 'address',
             gw_mac_address, run_as_root=True)
    _execute('ip', 'link', 'set', 'dev', bridge, 'address', gw_mac_address,
             run_as_root=True)
    _execute('ip', 'link', 'set', 'dev', dev, 'address', bridge_mac_address,
             run_as_root=True)

    _execute('ip', 'link', 'set', 'dev', enslaved_device, 'up', run_as_root=True)
    _execute('ip', 'link', 'set', 'dev', bridge, 'up', run_as_root=True)
    _execute('ip', 'link', 'set', 'dev', dev, 'up', run_as_root=True)

    dev = bridge

    out, err = _execute('ip', 'addr', 'show', 'dev', dev,
                        'scope', 'global', run_as_root=True)
    for line in out.split('\n'):
        fields = line.split()
        if fields and fields[0] == 'inet':
            ip_params = fields[1:-1]
            old_ip_params.append(ip_params)
            if ip_params[0] != full_ip:
                new_ip_params.append(ip_params)
    if not old_ip_params or old_ip_params[0][0] != full_ip:
        gateway = None
        out, err = _execute('route', '-n', run_as_root=True)
        for line in out.split('\n'):
            fields = line.split()
            if fields and fields[0] == '0.0.0.0' and \
                            fields[-1] == dev:
                gateway = fields[1]
                _execute('route', 'del', 'default', 'gw', gateway,
                         'dev', dev, check_exit_code=False,
                         run_as_root=True)
        for ip_params in old_ip_params:
            _execute(*_ip_bridge_cmd('del', ip_params, dev),
                        run_as_root=True)
        for ip_params in new_ip_params:
            _execute(*_ip_bridge_cmd('add', ip_params, dev),
                        run_as_root=True)
        if gateway:
            _execute('route', 'add', 'default', 'gw', gateway,
                        run_as_root=True)
        if FLAGS.send_arp_for_ha:
            _execute('arping', '-U', network_ref['dhcp_server'],
                      '-A', '-I', dev,
                      '-c', 1, run_as_root=True, check_exit_code=False)
    if(FLAGS.use_ipv6):
        _execute('ip', '-f', 'inet6', 'addr',
                     'change', network_ref['cidr_v6'],
                     'dev', dev, run_as_root=True)
    if(FLAGS.public_interface == dev):
        _execute('ip', 'link', 'set',
                     'dev', dev, 'promisc', 'on', run_as_root=True)


def initialize_gateway_device(dev, network_ref):
    gw_init_thread = Thread(target=_initialize_gateway_device,
                            args=(dev, network_ref,))
    gw_init_thread.start()
    LOG.debug("Gateway initalization thread started")


# plugs interfaces using Linux Bridge when using QuantumManager
class QuantumLibvirtLinuxBridgeDriver(LinuxNetInterfaceDriver):

    def plug(self, network, mac_address, gateway=True):
        dev = self.get_dev(network)
        if not _device_exists(dev):
            bridge = self.get_bridge(network)
            try:
                # First, try with 'ip'
                utils.execute('ip', 'tuntap', 'add', dev, 'mode', 'tap',
                          run_as_root=True)
            except exception.ProcessExecutionError:
                # Second option: tunctl
                utils.execute('tunctl', '-b', '-t', dev, run_as_root=True)
            utils.execute('ip', 'link', 'set', dev, "address", mac_address,
                          run_as_root=True)
            utils.execute('ip', 'link', 'set', dev, 'up', run_as_root=True)
            if not gateway:
                # If we weren't instructed to act as a gateway then add the
                # appropriate flows to block all non-dhcp traffic.
                # .. and make sure iptbles won't forward it as well.
                iptables_manager.ipv4['filter'].add_rule('FORWARD',
                        '--in-interface %s -j DROP' % bridge)
                iptables_manager.ipv4['filter'].add_rule('FORWARD',
                        '--out-interface %s -j DROP' % bridge)
            else:
                iptables_manager.ipv4['filter'].add_rule('FORWARD',
                        '--in-interface %s -j ACCEPT' % bridge)
                iptables_manager.ipv4['filter'].add_rule('FORWARD',
                        '--out-interface %s -j ACCEPT' % bridge)

        return dev

    def unplug(self, network):
        dev = self.get_dev(network)
        try:
            utils.execute('ip', 'link', 'delete', dev, run_as_root=True)
        except exception.ProcessExecutionError:
            LOG.warning(_("Failed while unplugging gateway interface '%s'"),
                        dev)
            raise
        LOG.debug(_("Unplugged gateway interface '%s'"), dev)
        return dev

    def get_dev(self, network):
        dev = GATEWAY_INTERFACE_PREFIX + str(network['uuid'][0:11])
        return dev

    def get_bridge(self, network):
        bridge = BRDIGE_NAME_PREFIX + str(network['uuid'][0:11])
        return bridge


if __name__ == "__main__":
    network_ref = {}
    network_ref['dhcp_server'] = "10.0.0.1"
    network_ref['uuid'] = '5c843d42-d2c2-45bf-8f48-9e7d5374933c'
    network_ref['cidr'] = '10.0.0.0/24'
    network_ref['broadcast'] = '255.255.255.0'
    initialize_gateway_device("gw-5c843d42-d2", network_ref)
