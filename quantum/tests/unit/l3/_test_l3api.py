# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2011, Cisco Systems, Inc.
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
#    @author: Sumit Naiksatam, Cisco Systems, Inc.

import logging
import unittest

from quantum import api as server
from quantum.plugins.l3.db import l3network_db as db
from quantum.tests.unit.l3.l3_test_lib import test_config
from quantum.wsgi import XMLDeserializer, JSONDeserializer


LOG = logging.getLogger(__name__)


RESPONSE_CODE_CREATE = 202
RESPONSE_CODE_UPDATE = 204
RESPONSE_CODE_DELETE = 204
RESPONSE_CODE_OTHERS = 200


XMLNS_KEY = 'xmlns'


class L3AbstractAPITest(unittest.TestCase):

    def _remove_non_attribute_keys(self, data_dict):
        if XMLNS_KEY  in data_dict.keys():
            data_dict.pop(XMLNS_KEY)
        return data_dict

    def setUp(self, api_router_klass, xml_metadata_dict):
        options = {}
        options['plugin_provider'] = test_config['plugin_name']
        options['plugin_l3provider'] = test_config['l3plugin_name']
        self.api = server.APIRouterV11(options)

    def tearDown(self):
        """Clear the test environment"""
        # Remove database contents
        db.clear_db()
