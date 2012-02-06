# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2011 Citrix Systems
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
# @author: Salvatore Orlando, Citrix Systems
# @author: Sumit Naiksatam, Cisco Systems, Inc.

"""
Quantum API controllers.
"""

import logging
import routes
import webob.dec
import webob.exc

from quantum import manager
from quantum.api import attachments
from quantum.api import networks
from quantum.api import ports
from quantum.api import subnets
from quantum.api import routetables
from quantum.api import l3routes
from quantum.api import targets
from quantum.api import associations
from quantum.common import flags
from quantum import wsgi


LOG = logging.getLogger('quantum.api')
FLAGS = flags.FLAGS


class APIRouter(wsgi.Router):
    """
    Base class for Quantum API routes.
    """

    def __init__(self, options=None):
        mapper = self._mapper()
        self._setup_routes(mapper, options)
        super(APIRouter, self).__init__(mapper)

    def _mapper(self):
        return routes.Mapper()

    def _setup_routes(self, mapper, options):
        self._setup_base_routes(mapper, options, self._version)

    def _setup_base_routes(self, mapper, options, version):
        """Routes common to all versions."""
        # Loads the quantum plugin
        # Note(salvatore-orlando): Should the plugin be versioned
        # I don't think so
        plugin = manager.QuantumManager.get_plugin(options)

        uri_prefix = '/tenants/{tenant_id}/'
        mapper.resource('network', 'networks',
                        controller=networks.create_resource(plugin, version),
                        collection={'detail': 'GET'},
                        member={'detail': 'GET'},
                        path_prefix=uri_prefix)
        mapper.resource('port', 'ports',
                        controller=ports.create_resource(plugin, version),
                        collection={'detail': 'GET'},
                        member={'detail': 'GET'},
                        parent_resource=dict(member_name='network',
                                             collection_name=uri_prefix +\
                                                 'networks'))
        attachments_ctrl = attachments.create_resource(plugin, version)
        mapper.connect("get_resource",
                       uri_prefix + 'networks/{network_id}/' \
                                    'ports/{id}/attachment{.format}',
                       controller=attachments_ctrl,
                       action="get_resource",
                       conditions=dict(method=['GET']))
        mapper.connect("attach_resource",
                       uri_prefix + 'networks/{network_id}/' \
                                    'ports/{id}/attachment{.format}',
                       controller=attachments_ctrl,
                       action="attach_resource",
                       conditions=dict(method=['PUT']))
        mapper.connect("detach_resource",
                       uri_prefix + 'networks/{network_id}/' \
                                    'ports/{id}/attachment{.format}',
                       controller=attachments_ctrl,
                       action="detach_resource",
                       conditions=dict(method=['DELETE']))


class APIRouterV10(APIRouter):
    """
    API routes mappings for Quantum API v1.0
    """
    _version = '1.0'


class APIRouterV11(APIRouter):
    """
    API routes mappings for Quantum API v1.1
    """
    _version = '1.1'

    def _setup_base_routes(self, mapper, options, version):
        """Routes specific to 1.1 version."""
        super(APIRouterV11, self)._setup_base_routes(mapper, options,
                                                     version)
        l3plugin = manager.QuantumManager.get_l3plugin(options)

        uri_prefix = '/tenants/{tenant_id}/'

        mapper.resource('subnet', 'subnets',
                        controller=subnets.create_resource(l3plugin, version),
                        collection={'detail': 'GET'},
                        member={'detail': 'GET'},
                        path_prefix=uri_prefix)

        mapper.resource('routetable', 'routetables',
                        controller=routetables.create_resource(l3plugin,
                                                               version),
                        collection={'detail': 'GET'},
                        member={'detail': 'GET'},
                        path_prefix=uri_prefix)

        l3routes_ctrl = l3routes.create_resource(l3plugin, version)
        mapper.resource('route', 'routes',
                        controller=l3routes_ctrl,
                        collection={'detail': 'GET'},
                        member={'detail': 'GET'},
                        parent_resource=dict(member_name='routetable',
                                             collection_name=uri_prefix +\
                                                 'routetables'))

        targets_ctrl = targets.create_resource(l3plugin, version)
        mapper.connect("get_all_targets",
                       uri_prefix + 'routetables/{routetable_id}/' \
                                    'targets{.format}',
                       controller=targets_ctrl,
                       action="get_all_targets",
                       conditions=dict(method=['GET']))

        associations_ctrl = associations.create_resource(l3plugin, version)
        mapper.connect("get_subnet_association",
                       uri_prefix + 'subnets/{subnet_id}/' \
                                    'association{.format}',
                       controller=associations_ctrl,
                       action="get_subnet_association",
                       conditions=dict(method=['GET']))
        mapper.connect("associate_subnet",
                       uri_prefix + 'subnets/{subnet_id}/' \
                                    'association{.format}',
                       controller=associations_ctrl,
                       action="associate_subnet",
                       conditions=dict(method=['PUT']))
        mapper.connect("disassociate_subnet",
                       uri_prefix + 'subnets/{subnet_id}/' \
                                    'association{.format}',
                       controller=associations_ctrl,
                       action="disassociate_subnet",
                       conditions=dict(method=['DELETE']))
        """
        mapper.connect("create",
                       uri_prefix + 'routetables/{routetable_id}/' \
                                    'routes{.format}',
                       controller=l3routes_ctrl,
                       action="create",
                       conditions=dict(method=['POST']))
        mapper.connect("delete",
                       uri_prefix + 'routetables/{routetable_id}/' \
                                    'routes{.format}',
                       controller=l3routes_ctrl,
                       action="delete",
                       conditions=dict(method=['DELETE']))
        mapper.connect("index",
                       uri_prefix + 'routetables/{routetable_id}/' \
                                    'routes{.format}',
                       controller=l3routes_ctrl,
                       action="index",
                       conditions=dict(method=['GET']))
        """
