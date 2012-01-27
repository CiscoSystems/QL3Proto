# vim: tabstop=4 shiftwidth=4 softtabstop=4
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
import subprocess
from netaddr import *

from quantum.common import exceptions as exc


LOG = logging.getLogger(__name__)
MINIMUM_IPS = 2


def validate_cidr(cidr):
    """
    This method returns True if the cidr is valid
    """
    try:
        return IPNetwork(cidr)
    except:
        raise exc.InvalidCIDR(cidr=cidr)


def validate_subnet_cidr(cidr):
    """
    This method returns True if the cidr is valid and it has more than
    two IPs.
    """
    try:
        return IPNetwork(cidr).size > MINIMUM_IPS
    except:
        raise exc.InvalidCIDR(cidr=cidr)
