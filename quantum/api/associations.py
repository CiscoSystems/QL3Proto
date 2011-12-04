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


class Controller(common.QuantumController):
    """ Associations API controller for Quantum API """

    _attachment_ops_param_list = [{
        'param-name': 'routetable_id',
        'required': True}, ]

    _serialization_metadata = {
        "application/xml": {
            "attributes": {
                "association": ["routetable_id"]}
        },
    }

    def __init__(self, plugin):
        self._resource_name = 'association'
        super(Controller, self).__init__(plugin)

    def get_subnet_association(self, request, tenant_id, subnet_id):
        try:
            data = self._plugin.get_subnet_association(tenant_id,
                                                         subnet_id)
            builder = associations_view.get_view_builder(request)
            result = builder.build(data)['association']
            return dict(association=result)
        except exception.SubnetNotFound as e:
            return faults.Fault(faults.SubnetNotFound(e))

    def associate_subnet(self, request, tenant_id, subnet_id):
        try:
            request_params = \
                self._parse_request_params(request,
                                           self._attachment_ops_param_list)
        except exc.HTTPError as e:
            return faults.Fault(e)
        try:
            LOG.debug("Associating subnet: %s with Route-table: %s",
                      (subnet_id, request_params['routetable_id']))
            self._plugin.associate_subnet(tenant_id, subnet_id,
                                          request_params['routetable_id'])
            return exc.HTTPNoContent()
        except exception.SubnetNotFound as e:
            return faults.Fault(faults.SubnetNotFound(e))
        except exception.RoutetableNotFound as e:
            return faults.Fault(faults.RoutetableNotFound(e))
        except exception.SubnetAlreadyAssociated as e:
            return faults.Fault(faults.SubnetAlreadyAssociated(e))

    def disassociate_subnet(self, request, tenant_id, subnet_id):
        try:
            data = self._plugin.disassociate_subnet(tenant_id, subnet_id)
            builder = associations_view.get_view_builder(request)
            result = builder.build(data)['association']
            return dict(association=result)
        except exception.SubnetNotFound as e:
            return faults.Fault(faults.SubnetNotFound(e))
        except exception.RoutetableNotFound as e:
            return faults.Fault(faults.RoutetableNotFound(e))
