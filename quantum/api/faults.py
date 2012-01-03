# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 Citrix Systems.
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


import webob.exc

from quantum.common import exceptions

_NETNOTFOUND_EXPL = 'Unable to find a network with the specified identifier.'
_NETINUSE_EXPL = 'Unable to remove the network: attachments still plugged.'
_PORTNOTFOUND_EXPL = 'Unable to find a port with the specified identifier.'
_STATEINVALID_EXPL = 'Unable to update port state with specified value.'
_PORTINUSE_EXPL = 'A resource is currently attached to the logical port'
_ALREADYATTACHED_EXPL = 'The resource is already attached to another port'
_SUBNETNOTFOUND_EXPL = 'Unable to find a subnet with the specified identifier'
_INVALIDCIDR_EXPL = 'Invalid CIDR provided'
_DUPLICATECIDR_EXPL = 'A subnet with this CIDR already exists for this tenant'
_SUBNETALREADYASSOCIATED_EXPL = \
        'Subnet is already associated with another Route-table'
_ROUTETABLENOTFOUND_EXPL = \
        'Unable to find a route table with the specified identifier'
_ROUTENOTFOUND_EXPL = 'Unable to find a route in the route table'
_ROUTESOURCEINVALID_EXPL = 'Unable to resolve route source identifier'
_ROUTEDESTINATIONINVALID_EXPL = \
        'Unable to resolve route destination identifier'
_ROUTETARGETINVALID_EXPL = 'Unable to resolve route target identifier'


class QuantumHTTPError(webob.exc.HTTPClientError):

    _fault_dict = {
            exceptions.NetworkNotFound: {
                'code': 420,
                'title': 'networkNotFound',
                'explanation': _NETNOTFOUND_EXPL
            },
            exceptions.NetworkInUse: {
                'code': 421,
                'title': 'networkInUse',
                'explanation': _NETINUSE_EXPL
            },
            exceptions.PortNotFound: {
                'code': 430,
                'title': 'portNotFound',
                'explanation': _PORTNOTFOUND_EXPL
            },
            exceptions.StateInvalid: {
                'code': 431,
                'title': 'requestedStateInvalid',
                'explanation': _STATEINVALID_EXPL
            },
            exceptions.PortInUse: {
                'code': 432,
                'title': 'portInUse',
                'explanation': _PORTINUSE_EXPL
            },
            exceptions.AlreadyAttached: {
                'code': 440,
                'title': 'alreadyAttached',
                'explanation': _ALREADYATTACHED_EXPL
            },
            exceptions.SubnetNotFound: {
                'code': 450,
                'title': 'Subnet not Found',
                'explanation': _SUBNETNOTFOUND_EXPL
            },
            exceptions.InvalidCIDR: {
                'code': 451,
                'title': 'Invalid CIDR',
                'explanation': _INVALIDCIDR_EXPL
            },
            exceptions.DuplicateCIDR: {
                'code': 452,
                'title': 'Duplicate CIDR',
                'explanation': _DUPLICATECIDR_EXPL
            },
            exceptions.SubnetAlreadyAssociated: {
                'code': 453,
                'title': 'Subnet already associated',
                'explanation': _SUBNETALREADYASSOCIATED_EXPL
            },
            exceptions.RoutetableNotFound: {
                'code': 460,
                'title': 'Route Table not Found',
                'explanation': _ROUTETABLENOTFOUND_EXPL
            },
            exceptions.RouteNotFound: {
                'code': 465,
                'title': 'Route not Found',
                'explanation': _ROUTENOTFOUND_EXPL
            },
            exceptions.RouteSourceInvalid: {
                'code': 466,
                'title': 'Route Source Invalid',
                'explanation': _ROUTESOURCEINVALID_EXPL
            },
            exceptions.RouteDestinationInvalid: {
                'code': 467,
                'title': 'Route Destination Invalid',
                'explanation': _ROUTEDESTINATIONINVALID_EXPL
            },
            exceptions.RouteTargetInvalid: {
                'code': 468,
                'title': 'Route Target Invalid',
                'explanation': _ROUTETARGETINVALID_EXPL
            }
    }

    def __init__(self, inner_exc):
        _fault_data = self._fault_dict.get(type(inner_exc), None)
        if _fault_data:
            self.code = _fault_data['code']
            self.title = _fault_data['title']
            self.explanation = _fault_data['explanation']
        super(webob.exc.HTTPClientError, self).__init__(inner_exc)
