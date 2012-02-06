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
#
# @author Sumit Naiksatam
#

import logging

from webob import exc

from quantum.api import api_common as common
from quantum.api import faults
from quantum.api.views import associations as associations_view
from quantum.common import exceptions as exception

LOG = logging.getLogger('quantum.api.associations')


def create_resource(plugin, version):
    controller_dict = {
                        '1.1': [ControllerV11(plugin),
                                ControllerV11._serialization_metadata,
                                common.XML_NS_V11]}
    return common.create_resource(version, controller_dict)


class Controller(common.QuantumController):
    """ Associations API controller for Quantum API """

    _attachment_ops_param_list = [{
        'param-name': 'routetable_id',
        'required': True}, ]

    def __init__(self, plugin):
        self._resource_name = 'association'
        super(Controller, self).__init__(plugin)

    @common.APIFaultWrapper([exception.SubnetNotFound])
    def get_subnet_association(self, request, tenant_id, subnet_id):
        data = self._plugin.get_subnet_association(tenant_id,
                                                     subnet_id)
        builder = associations_view.get_view_builder(request, self.version)
        result = builder.build(data)['association']
        return dict(association=result)

    @common.APIFaultWrapper([exception.SubnetNotFound,
                             exception.RoutetableNotFound,
                             exception.SubnetAlreadyAssociated])
    def associate_subnet(self, request, tenant_id, subnet_id, body):
        body = self._prepare_request_body(body,
                                          self._attachment_ops_param_list)
        LOG.debug("associate_subnet() body: %s" % body)
        LOG.debug("Associating subnet: %s with Route-table: %s" % \
                  (subnet_id, body['association']['routetable_id']))

        data = self.\
                _plugin.associate_subnet(tenant_id,
                                         subnet_id,
                                         body['association']['routetable_id'])

        builder = associations_view.get_view_builder(request, self.version)
        result = builder.build(data)['association']
        return dict(association=result)

    @common.APIFaultWrapper([exception.SubnetNotFound,
                             exception.RoutetableNotFound])
    def disassociate_subnet(self, request, tenant_id, subnet_id):
        LOG.debug("disassociate_subnet() body: %s" % subnet_id)
        data = self._plugin.disassociate_subnet(tenant_id, subnet_id)
        builder = associations_view.get_view_builder(request, self.version)
        result = builder.build(data)['association']
        return dict(association=result)


class ControllerV11(Controller):
    """Association resources controller for Quantum v1.1 API
    """

    _serialization_metadata = {
            "attributes": {
                "association": ["routetable_id"]}
    }

    def __init__(self, plugin):
        self.version = "1.1"
        super(ControllerV11, self).__init__(plugin)
