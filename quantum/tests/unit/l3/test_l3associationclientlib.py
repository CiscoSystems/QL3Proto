# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
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
#    @author: Atul Gaikwad, Cisco Systems
"""Testing L3 Association CLI"""

import logging
import unittest
import re

from quantum.common.serializer import Serializer
from quantum.client.l3client.l3client import Client
from quantum.tests.unit.l3.test_l3clientlib import *

LOG = logging.getLogger(__name__)


class L3AssociationCLIAPITest(L3CLIAPITest):
    """L3 Association tests class"""
    def _test_show_association(self, tenant=TENANT_1, format='json',
                               status=200):
        """Test to show available association"""
        LOG.debug("_test_show_association - tenant:%s "\
                  "- format:%s - START", format, tenant)

        self._assert_sanity(self.client.show_subnet_association,
                            status,
                            "GET",
                            "subnets/001/association",
                            data=["001"],
                            params={'tenant': tenant, 'format': format})

        LOG.debug("_test_show_association - tenant:%s "\
                  "- format:%s - END", format, tenant)

    def _test_create_association(self, tenant=TENANT_1,
                                 format='json', status=200):
        """Test creating a new association"""
        LOG.debug("_test_create_association - tenant:%s "\
                  "- format:%s - START", format, tenant)

        self._assert_sanity(self.client.associate_subnet,
                            status,
                            "PUT",
                            "subnets/001/association",
                            data=["001"],
                            params={'tenant': tenant, 'format': format})

        LOG.debug("_test_create_association - tenant:%s "\
                  "- format:%s - END", format, tenant)

    def _test_delete_association(self, tenant=TENANT_1,
                                 format='json', status=200):
        """Test deleting association"""
        LOG.debug("_test_delete_association - tenant:%s "\
                  "- format:%s - START", format, tenant)

        self._assert_sanity(self.client.disassociate_subnet,
                            status,
                            "DELETE",
                            "subnets/001/association",
                            data=["001"],
                            params={'tenant': tenant, 'format': format})

        LOG.debug("_test_delete_association - tenant:%s "\
                  "- format:%s - END", format, tenant)

    def test_show_association_json(self):
        """Test to show available association with json"""
        self._test_show_association(format='json')

    def test_show_association_xml(self):
        """Test to show available association with xml"""
        self._test_show_association(format='xml')

    def test_show_assoc_alt_tenant(self):
        """Test to show available association with alternate tenant"""
        self._test_show_association(tenant=TENANT_2)

    def test_show_association_error_470(self):
        """Test to show available association for error 470"""
        self._test_show_association(status=470)

    def test_show_association_error_401(self):
        """Test to show available association for error 401"""
        self._test_show_association(status=401)

    def test_show_association_error_450(self):
        """Test to show available association for error 450"""
        self._test_show_association(status=450)

    def test_create_association_json(self):
        """Test creating association with json"""
        self._test_create_association(format='json')

    def test_create_association_xml(self):
        """Test creating association with xml"""
        self._test_create_association(format='xml')

    def test_create_assoc_alt_tenant(self):
        """Test creating association with alternate tenant"""
        self._test_create_association(tenant=TENANT_2)

    def test_create_assoc_error_470(self):
        """Test creating association for error 470"""
        self._test_create_association(status=470)

    def test_create_assoc_error_401(self):
        """Test creating association for error 401"""
        self._test_create_association(status=401)

    def test_create_assoc_error_400(self):
        """Test creating association for error 400"""
        self._test_create_association(status=400)

    def test_delete_association_json(self):
        """Test deleting association with json"""
        self._test_delete_association(format='json')

    def test_delete_association_xml(self):
        """Test deleting association with xml"""
        self._test_delete_association(format='xml')

    def test_delete_assoc_alt_tenant(self):
        """Test deleting association with alternate tenant"""
        self._test_delete_association(tenant=TENANT_2)

    def test_delete_assoc_error_470(self):
        """Test deleting association for error 470"""
        self._test_delete_association(status=470)

    def test_delete_assoc_error_401(self):
        """Test deleting association for error 401"""
        self._test_delete_association(status=401)

    def test_delete_assoc_error_450(self):
        """Test deleting association for error 450"""
        self._test_delete_association(status=450)

    def test_delete_assoc_error_451(self):
        """Test deleting association for error 451"""
        self._test_delete_association(status=451)
