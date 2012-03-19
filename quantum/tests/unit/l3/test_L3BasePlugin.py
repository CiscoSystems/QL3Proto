# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2011, Cisco Systems, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
# @author: Shubhangi Satras, Cisco Systems, Inc.
# @author: Peter Strunk, Cisco Systems, Inc.
# @author: Atul Gaikwad, Cisco Systems, Inc.
"""Class for Testting L3BasePlugin functions"""


import unittest
import logging as LOG
from quantum.plugins.l3 import L3BasePlugin
from quantum.common.l3 import l3exceptions as exc
from quantum.db.l3 import api as api
from quantum.plugins.l3.db import l3network_db as db


class L3BaseTestPlugin(unittest.TestCase):
    """
    Unit Tests for the L3BasePlugin functions
    """

    def setUp(self):
        """
        The test runner will run this method prior to each test\
        General parameters required by all tests have been set here
        """
        self.L3BasePlugin = L3BasePlugin.L3BasePlugin()
        self.tenant_id = "test_tenant_cisco"
        self.cidr = "10.0.0.0/24"
        self.source = "10.0.0.0/24"
        self.destination = "0.0.0.0"
        subnet_data = self.L3BasePlugin.create_subnet(self.tenant_id,
                                                      self.cidr)
        self.subnet_id = subnet_data['subnet_id']
        routetable_data = self.L3BasePlugin.create_routetable(self.tenant_id)
        self.routetable_id = routetable_data['routetable_id']

    def test_invalidsubnetcidr_create_subnet(self):
        """
        Negative Test to check the Validity of CIDR while creating\
        subnet.
        """
        LOG.debug("test_invalidsubnetcidr_create_subnet - START")
        invalidcidr = "10.0.0.0/31"
        self.assertRaises(exc.InvalidCIDR,
                          self.L3BasePlugin.create_subnet,
                          self.tenant_id, invalidcidr)
        LOG.debug("test_invalidsubnetcidr_create_subnet - END")

    def test_invalidcidr_create_subnet(self):
        """
        Negative Test to check the Validity of CIDR while creating\
        subnet
        """
        LOG.debug("test_invalidcidr_create_subnet - START")
        invalidcidr = "6000.0.0/24"
        self.assertRaises(exc.InvalidCIDR,
                          self.L3BasePlugin.create_subnet,
                          self.tenant_id, invalidcidr)
        LOG.debug("test_invalidcidr_create_subnet - END")

    def test_duplicate_subnet_cidr(self):
        """
        Negative Test to check Duplicate CIDR
        """
        LOG.debug("test_duplicate_subnet_cidr - START")
        self.assertRaises(exc.DuplicateCIDR,
                          api._check_duplicate_cidr,
                          self.tenant_id, self.cidr)
        LOG.debug("test_duplicate_subnet_cidr - END")

    def test_duplicate_cidr_create_subnet(self):
        """
        Negative Test to check Duplicate CIDR while creating subnet
        """
        LOG.debug("test_duplicate_cidr_create_subnet - START")
        self.assertRaises(exc.DuplicateCIDR,
                          self.L3BasePlugin.create_subnet,
                          self.tenant_id, self.cidr)
        LOG.debug("test_duplicate_cidr_create_subnet - END")

    def test_duplicate_cidr_update_subnet(self):
        """
        Negative Test to check Duplicate CIDR while updating subnet
        """
        LOG.debug("test_duplicate_cidr_update_subnet - START")
        self.assertRaises(exc.DuplicateCIDR,
                          self.L3BasePlugin.update_subnet,
                          self.tenant_id, self.subnet_id, cidr=self.cidr)
        LOG.debug("test_duplicate_cidr_update_subnet - END")

    def test_invalidsubnetcidr_update_subnet(self):
        """
        Negative Test to check the Validity of CIDR while updating subnet
        """
        LOG.debug("test_invalidsubnetcidr_update_subnet - START")
        invalidcidr = "10.0.0.0/31"
        self.assertRaises(exc.InvalidCIDR,
                          self.L3BasePlugin.update_subnet,
                          self.subnet_id, self.tenant_id, cidr=invalidcidr)
        LOG.debug("test_invalidsubnetcidr_update_subnet - END")

    def test_invalidcidr_update_subnet(self):
        """
        Negative Test to check the Validity of CIDR while creating subnet
        """
        LOG.debug("test_duplicate_cidr_create_subnet - END")
        invalidcidr = "6000.0.0/24"
        self.assertRaises(exc.InvalidCIDR,
                          self.L3BasePlugin.update_subnet,
                          self.tenant_id, self.subnet_id, cidr=invalidcidr)

    def test_update_subnet_not_found(self):
        """
        Negative Test to check whether the Exception in raised when subnet\
        does not exist and update subnet is issued.
        """
        subnet_id = "f1234567-1234-1234-1234-123456789012"
        self.assertRaises(exc.SubnetNotFound,
        self.L3BasePlugin.update_subnet,
        self.tenant_id, subnet_id, cidr=self.cidr)

    def test_delete_subnet_not_found(self):
        """
        Negative Test to check Exception being raised Subnet Not Found
        """
        subnet_id = "f1234567-1234-1234-1234-123456789012"
        self.assertRaises(exc.SubnetNotFound,
        self.L3BasePlugin.delete_subnet,
        self.tenant_id, subnet_id)

    def test_delete_routetablenotfound(self):
        """
        Negative Test to Check whether Exception  is being raised\
        for Routetable not found
        """
        routetable_id = "f1234567-1234-1234-1234-123456789012"
        self.assertRaises(exc.RoutetableNotFound,
        self.L3BasePlugin.delete_routetable,
        self.tenant_id, routetable_id)

    def test_update_routetablenotfound(self):
        """
        Negative Test to Check whether Exception  is being raised\
        for Routetable not found while updating routetable
        """
        routetable_id = "f1234567-1234-1234-1234-123456789012"
        self.assertRaises(exc.RoutetableNotFound,
        self.L3BasePlugin.update_routetable,
        self.tenant_id, routetable_id)

    def _test_validate_route_source(self, source, exception):
        """
        Validate source for ROUTES
        """
        LOG.debug("BEGIN - _test_validate_route_source")
        self.L3BasePlugin.associate_subnet(self.tenant_id,
                                           self.subnet_id,
                                           self.routetable_id)
        target_data = self.L3BasePlugin.get_all_targets(self.tenant_id,
                                                        self.routetable_id)
        target_tag = target_data[0]['target']
        self.assertRaises(exception, self.L3BasePlugin.create_route,
                          self.tenant_id, self.routetable_id,
                          source, self.destination,
                          target_tag)
        LOG.debug("END - _test_validate_route_source")

    def _test_validate_route_destination(self, destination, exception):
        """
        Validate destination for ROUTES
        """
        LOG.debug("BEGIN - _test_validate_route_destination")
        self.L3BasePlugin.associate_subnet(self.tenant_id,
                                           self.subnet_id,
                                           self.routetable_id)
        target_data = self.L3BasePlugin.get_all_targets(self.tenant_id,
                                                        self.routetable_id)
        target_tag = target_data[0]['target']
        self.assertRaises(exception, self.L3BasePlugin.create_route,
                          self.tenant_id, self.routetable_id,
                          self.source, destination,
                          target_tag)
        LOG.debug("END - _test_validate_route_destination")

    def _test_validate_route_target(self, target, exception):
        """
        Validate target for ROUTES
        """
        LOG.debug("BEGIN - _test_validate_route_target")
        self.L3BasePlugin.associate_subnet(self.tenant_id,
                                           self.subnet_id,
                                           self.routetable_id)
        self.assertRaises(exception, self.L3BasePlugin.create_route,
                          self.tenant_id, self.routetable_id,
                          self.source, self.destination,
                          target)
        LOG.debug("END - _test_validate_route_target")

    def test_check_duplicate_route(self):
        """
        Validate target for ROUTES
        """
        LOG.debug("BEGIN - _test_check_duplicate_route")
        self.L3BasePlugin.associate_subnet(self.tenant_id,
                                           self.subnet_id,
                                           self.routetable_id)
        target_data = self.L3BasePlugin.get_all_targets(self.tenant_id,
                                                        self.routetable_id)
        target_tag = target_data[0]['target']
        route_data = self.L3BasePlugin.create_route(self.tenant_id,
                                       self.routetable_id,
                                       self.source, self.destination,
                                       target_tag)
        route_id = route_data['route_id']
        self.assertRaises(exc.DuplicateRoute, self.L3BasePlugin.create_route,
                          self.tenant_id, self.routetable_id,
                          self.source, self.destination, target_tag)
        self.L3BasePlugin.delete_route(self.tenant_id, self.routetable_id,
                                       route_id)
        self.tearDown()
        LOG.debug("END - _test_check_duplicate_route")

    def test_check_rt_not_found(self):
        """
        check exception RouteNotFound
        """
        LOG.debug("BEGIN - test_check_rt_not_found")
        self.L3BasePlugin.associate_subnet(self.tenant_id,
                                           self.subnet_id,
                                           self.routetable_id)
        route_id = ''
        self.assertRaises(exc.RouteNotFound, self.L3BasePlugin.delete_route,
                          self.tenant_id, self.routetable_id, route_id)
        self.tearDown()
        LOG.debug("END - test_check_rt_not_found")

    def test_val_rt_src_badCIDR(self):
        """
        Gives invalid cidr to validate_route_source
        """
        bad_cidr = ''
        self._test_validate_route_source(bad_cidr, exc.InvalidCIDR)
        self.tearDown()

    def test_val_rt_src_invalid(self):
        """
        Gives invalid source
        """
        source = '10.10.10.10/24'
        self._test_validate_route_source(source, exc.RouteSourceInvalid)

    def test_val_rt_dest_badCIDR(self):
        """
        Gives invalid cidr to validate_route_destination
        """
        bad_cidr = ''
        self._test_validate_route_destination(bad_cidr, exc.InvalidCIDR)
        self.tearDown()

    #This test needs a fix
    #def test_val_rt_dest_invalid(self):
    #    """
    #    Gives invalid destination
    #    """
    #    destination = '2a39409c-7146-4501-8429-3579e03e9d76'
    #    self._test_validate_route_destination(destination,
    #                                          exc.RouteDestinationInvalid)
    #    self.tearDown()

    def test_val_rt_target_invalid(self):
        """
        Gives invalid target
        """
        target = 'bad_target'
        self._test_validate_route_target(target, exc.TargetNotFound)
        self.tearDown()

    def test_duplicate_target(self):
        """ Test to check for target duplication """
        """ L3BasePlugin.__init__ """
        LOG.debug("BEGIN - test_duplicate_target")
        tag = "tag_duplicate_target"
        db.target_create(tag.lower(), self.tenant_id)
        self.assertRaises(exc.DuplicateTarget, db.target_create,
                          tag.lower(), self.tenant_id)
        self.tearDown()
        LOG.debug("END - test_duplicate_target")

    def test_target_not_found(self):
        """ Test to check for target existence """
        LOG.debug("BEGIN - test_target_not_found")
        tag = "tag_target_not_found"
        self.assertRaises(exc.TargetNotFound,
                          db.target_get, tag.lower(),
                          self.tenant_id)
        self.tearDown()
        LOG.debug("END - test_target_not_found")

    def test_getsa_subnet_not_found(self):
        """ L3BasePlugin.get_subnet_association """
        """ Test to check if subnet not found """
        LOG.debug("BEGIN - test_getsa_subnet_not_found")
        tenant_id = "test11"
        subnet_id = "00000000-0000-0000-0000-000000000000"
        self.assertRaises(exc.SubnetNotFound,
                         self.L3BasePlugin.get_subnet_association, tenant_id,
                         subnet_id)
        self.tearDown()
        LOG.debug("END - test_getsa_subnet_not_found")

    def test_as_subnet_already_asso(self):
        """ L3BasePlugin.associate_subnet """
        """ Test to check if subnet association already exists """
        LOG.debug("BEGIN - test_as_subnet_already_asso")
        tenant_id = "test11"
        subnet_id = self.L3BasePlugin.create_subnet(
                    tenant_id, "90.0.0.0/24")["subnet_id"]
        routetable_id = self.L3BasePlugin.create_routetable(
                        tenant_id)["routetable_id"]
        self.L3BasePlugin.associate_subnet(tenant_id, subnet_id,
                                           routetable_id)
        self.assertRaises(exc.SubnetAlreadyAssociated,
                         self.L3BasePlugin.associate_subnet, tenant_id,
                         subnet_id, routetable_id)
        self.tearDown()
        LOG.debug("END - test_as_subnet_already_asso")

    def test_as_subnet_not_found(self):
        """ Test to check if subnet not found """
        """ L3BasePlugin.associate_subnet """
        LOG.debug("BEGIN - test_as_subnet_not_found")
        tenant_id = "test11"
        subnet_id = "00000000-0000-0000-0000-000000000000"
        routetable_id = self.L3BasePlugin.create_routetable(
                        tenant_id)["routetable_id"]
        self.assertRaises(exc.SubnetNotFound,
                          self.L3BasePlugin.associate_subnet, tenant_id,
                          subnet_id, routetable_id)
        self.tearDown()
        LOG.debug("END - test_as_subnet_not_found")

    def test_das_subnet_not_found(self):
        """ Test to check if subnet not found """
        """ L3BasePlugin.disassociate_subnet """
        LOG.debug("BEGIN - test_das_subnet_not_found")
        tenant_id = "test11"
        subnet_id = "00000000-0000-0000-0000-000000000000"
        self.assertRaises(exc.SubnetNotFound,
                          self.L3BasePlugin.disassociate_subnet, tenant_id,
                          subnet_id,)
        self.tearDown()
        LOG.debug("END - test_das_subnet_not_found")

    def tearDown(self):
        """
        tear down tests
        """
        LOG.debug("Tear Down function START")
        try:
            self.L3BasePlugin.disassociate_subnet(self.tenant_id,
                                                  self.subnet_id)
        except:
            pass
        try:
            self.L3BasePlugin.delete_routetable(self.tenant_id,
                                                self.routetable_id)
        except:
            pass
        try:
            self.L3BasePlugin.delete_subnet(self.tenant_id,
                                            self.subnet_id)
        except:
            pass
        LOG.debug("Tear Down function END")
