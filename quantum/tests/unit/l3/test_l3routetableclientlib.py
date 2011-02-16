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
#    @author: Sumit Naiksatam, Cisco Systems

import logging
import unittest
import re

from quantum.common.serializer import Serializer
from quantum.client.l3client.l3client import Client
from quantum.tests.unit.l3.test_l3clientlib import *

LOG = logging.getLogger(__name__)


class L3SRoutetableCLIAPITest(L3CLIAPITest):

    def _test_list_routetables(self, tenant=TENANT_1, format='json', status=200):
        LOG.debug("_test_list_routetable - tenant:%s "\
                  "- format:%s - START", format, tenant)

        self._assert_sanity(self.client.list_routetables,
                            status,
                            "GET",
                            "routetables",
                            data=[],
                            params={'tenant': tenant, 'format': format})

        LOG.debug("_test_list_routetables - tenant:%s "\
                  "- format:%s - END", format, tenant)

    def _test_show_routetable_details(self,
                                   tenant=TENANT_1, format='json', status=200):
        LOG.debug("_test_show_routetable_details - tenant:%s "\
                  "- format:%s - START", format, tenant)

        self._assert_sanity(self.client.show_routetable_details,
                            status,
                            "GET",
                            "routetables/001",
                            data=["001"],
                            params={'tenant': tenant, 'format': format})

        LOG.debug("_test_show_routetable_details - tenant:%s "\
                  "- format:%s - END", format, tenant)

    def _test_create_routetable(self, tenant=TENANT_1, format='json', status=200):
        LOG.debug("_test_create_routetable - tenant:%s "\
                  "- format:%s - START", format, tenant)

        self._assert_sanity(self.client.create_routetable,
                            status,
                            "POST",
                            "routetables",
                            data=[{'routetable': {}}],
                            params={'tenant': tenant, 'format': format})

        LOG.debug("_test_create_routetable - tenant:%s "\
                  "- format:%s - END", format, tenant)

    def _test_update_routetable(self, tenant=TENANT_1, format='json', status=200):
        LOG.debug("_test_update_routetable - tenant:%s "\
                  "- format:%s - START", format, tenant)

        self._assert_sanity(self.client.update_routetable,
                            status,
                            "PUT",
                            "routetables/001",
                            data=["001",
                                  {'routetable': {}}],
                            params={'tenant': tenant, 'format': format})

        LOG.debug("_test_update_routetable - tenant:%s "\
                  "- format:%s - END", format, tenant)

    def _test_delete_routetable(self, tenant=TENANT_1, format='json', status=200):
        LOG.debug("_test_delete_routetable - tenant:%s "\
                  "- format:%s - START", format, tenant)

        self._assert_sanity(self.client.delete_routetable,
                            status,
                            "DELETE",
                            "routetables/001",
                            data=["001"],
                            params={'tenant': tenant, 'format': format})

        LOG.debug("_test_delete_routetable - tenant:%s "\
                  "- format:%s - END", format, tenant)

    def test_list_routetables_json(self):
        self._test_list_routetables(format='json')

    def test_list_routetables_xml(self):
        self._test_list_routetables(format='xml')

    def test_list_routetables_alt_tenant(self):
        self._test_list_routetables(tenant=TENANT_2)

    def test_list_routetables_error_470(self):
        self._test_list_routetables(status=470)

    def test_list_routetables_error_401(self):
        self._test_list_routetables(status=401)

    def test_show_routetable_details_json(self):
        self._test_show_routetable_details(format='json')

    def test_show_routetable_details_xml(self):
        self._test_show_routetable_details(format='xml')

    def test_show_routetable_details_alt_tenant(self):
        self._test_show_routetable_details(tenant=TENANT_2)

    def test_show_routetable_details_error_470(self):
        self._test_show_routetable_details(status=470)

    def test_show_routetable_details_error_401(self):
        self._test_show_routetable_details(status=401)

    def test_show_routetable_details_error_450(self):
        self._test_show_routetable_details(status=450)

    def test_create_routetable_json(self):
        self._test_create_routetable(format='json')

    def test_create_routetable_xml(self):
        self._test_create_routetable(format='xml')

    def test_create_routetable_alt_tenant(self):
        self._test_create_routetable(tenant=TENANT_2)

    def test_create_routetable_error_470(self):
        self._test_create_routetable(status=470)

    def test_create_routetable_error_401(self):
        self._test_create_routetable(status=401)

    def test_create_routetable_error_400(self):
        self._test_create_routetable(status=400)

    def test_update_routetable_json(self):
        self._test_update_routetable(format='json')

    def test_update_routetable_xml(self):
        self._test_update_routetable(format='xml')

    def test_update_routetable_alt_tenant(self):
        self._test_update_routetable(tenant=TENANT_2)

    def test_update_routetable_error_470(self):
        self._test_update_routetable(status=470)

    def test_update_routetable_error_401(self):
        self._test_update_routetable(status=401)

    def test_update_routetable_error_400(self):
        self._test_update_routetable(status=400)

    def test_update_routetable_error_450(self):
        self._test_update_routetable(status=450)

    def test_delete_routetable_json(self):
        self._test_delete_routetable(format='json')

    def test_delete_routetable_xml(self):
        self._test_delete_routetable(format='xml')

    def test_delete_routetable_alt_tenant(self):
        self._test_delete_routetable(tenant=TENANT_2)

    def test_delete_routetable_error_470(self):
        self._test_delete_routetable(status=470)

    def test_delete_routetable_error_401(self):
        self._test_delete_routetable(status=401)

    def test_delete_routetable_error_450(self):
        self._test_delete_routetable(status=450)

    def test_delete_routetable_error_451(self):
        self._test_delete_routetable(status=451)
