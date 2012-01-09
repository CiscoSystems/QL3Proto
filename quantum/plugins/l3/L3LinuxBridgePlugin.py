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
# @author: Rohit Agarwalla, Cisco Systems, Inc.

import logging

from quantum.common import exceptions as exc
from quantum.db import api as db

from L3BasePlugin import *

LOG = logging.getLogger('quantum.plugins.L3LinuxBridgePlugin')


class L3LinuxBridgePlugin(L3BasePlugin):
    """
    L3 Plugin that leverages Linux Bridge
    """

    def __init__(self):
        super(L3LinuxBridgePlugin, self).__init__()
