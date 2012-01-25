# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 Cisco Systems
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
#    @author: Sumit Naiksatam, Cisco Systems

import logging
import unittest
import re

from quantum.common.serializer import Serializer
from quantum.client.l3client.l3client import Client

LOG = logging.getLogger(__name__)

# Set a couple tenants to use for testing
TENANT_1 = 'tenant1'
TENANT_2 = 'tenant2'


class ServerStub():
    """This class stubs a basic server for the API client to talk to"""

    class Response(object):
        """This class stubs a basic response to send the API client"""
        def __init__(self, content=None, status=None):
            self.content = content
            self.status = status

        def read(self):
            return self.content

        def status(self):
            return self.status

    # To test error codes, set the host to 10.0.0.1, and the port to the code
    def __init__(self, host, port=9696, key_file="", cert_file=""):
        self.host = host
        self.port = port
        self.key_file = key_file
        self.cert_file = cert_file

    def request(self, method, action, body, headers):
        self.method = method
        self.action = action
        self.body = body

    def status(self, status=None):
        return status or 200

    def getresponse(self):
        res = self.Response(status=self.status())

        # If the host is 10.0.0.1, return the port as an error code
        if self.host == "10.0.0.1":
            res.status = self.port
            return res

        # Extract important information from the action string to assure sanity
        match = re.search('tenants/(.+?)/(.+)\.(json|xml)$', self.action)

        tenant = match.group(1)
        path = match.group(2)
        format = match.group(3)

        data = {'data': {'method': self.method, 'action': self.action,
                         'body': self.body, 'tenant': tenant, 'path': path,
                         'format': format, 'key_file': self.key_file,
                         'cert_file': self.cert_file}}

        # Serialize it to the proper format so the API client can handle it
        if data['data']['format'] == 'json':
            res.content = Serializer().serialize(data, "application/json")
        else:
            res.content = Serializer().serialize(data, "application/xml")
        return res


class L3CLIAPITest(unittest.TestCase):

    def setUp(self):
        """ Setups a test environment for the API client """
        HOST = '127.0.0.1'
        PORT = 9696
        USE_SSL = False

        self.client = Client(HOST, PORT, USE_SSL, TENANT_1, 'json', ServerStub)

    def _assert_sanity(self, call, status, method, path, data=[], params={}):
        """ Perform common assertions to test the sanity of client requests """

        # Handle an error case first
        if status != 200:
            (self.client.host, self.client.port) = ("10.0.0.1", status)
            self.assertRaises(Exception, call, *data, **params)
            return

        # Make the call, then get the data from the root node and assert it
        data = call(*data, **params)['data']

        self.assertEqual(data['method'], method)
        self.assertEqual(data['format'], params['format'])
        self.assertEqual(data['tenant'], params['tenant'])
        self.assertEqual(data['path'], path)

        return data

