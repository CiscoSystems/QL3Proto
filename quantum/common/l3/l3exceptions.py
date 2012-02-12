# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2011 Cisco Systems, Inc
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

"""
L3 exceptions
"""

import logging
import gettext

from quantum.common.exceptions import QuantumException


gettext.install('quantum', unicode=1)


class SubnetNotFound(QuantumException):
    message = _("Subnet %(subnet_id)s could not be found")


class SubnetAlreadyAssociated(QuantumException):
    message = _("Subnet %(subnet_id)s is already associated with " \
                "Routetable %(routetable_id). To change association " \
                "first remove association and then try associating "\
                "again.")


class SubnetRouteError(QuantumException):
    message = _("Subnet %(subnet_id)s has routes associated with it." \
                "Remove these routes to dissassociate/delete this subnet.")


class InvalidCIDR(QuantumException):
    message = _("CIDR %(cidr)s is invalid")


class DuplicateCIDR(QuantumException):
    message = _("Subnet with CIDR %(cidr)s already exists")


class RoutetableNotFound(QuantumException):
    message = _("Routetable %(routetable_id)s could not be found")


class RoutetableRouteError(QuantumException):
    message = _("Routetable %(routetable_id)s has routes associated with it." \
                "Remove these routes to dissassociate/delete this routetable.")


class RouteNotFound(QuantumException):
    message = _("Route with routetable_id: %(routetable_id)s " \
                "route_id: %(route_id)s could not be found")


class RouteSourceInvalid(QuantumException):
    message = _("Source %(source_id)s is invalid")


class RouteDestinationInvalid(QuantumException):
    message = _("Destination %(destination_id)s is invalid")


class RouteTargetInvalid(QuantumException):
    message = _("Target %(target_id)s is invalid")


class DuplicateRoute(QuantumException):
    message = _("Route with Source:%(source)s Destination:%(destination)s " \
                "Target:%(target)s already exists")


class DuplicateTarget(QuantumException):
    message = _("Target with Tag:%(tag)s Tenant-Id:%(tenant_id)s " \
                "already exists")


class TargetNotFound(QuantumException):
    message = _("Target %(target_id)s could not be found in the System " \
                "Target Table")


def wrap_exception(f):
    def _wrap(*args, **kw):
        try:
            return f(*args, **kw)
        except Exception, e:
            if not isinstance(e, Error):
                #exc_type, exc_value, exc_traceback = sys.exc_info()
                logging.exception('Uncaught exception')
                #logging.error(traceback.extract_stack(exc_traceback))
                raise Error(str(e))
            raise
    _wrap.func_name = f.func_name
    return _wrap
