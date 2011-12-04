#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 Cisco Systems, Inc.
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

""" Functions providing implementation for CLI commands. """

import logging
import os
import sys

FORMAT = "json"
LOG = logging.getLogger('quantum.l3cli_lib')


class OutputTemplate(object):
    """ A class for generating simple templated output.
        Based on Python templating mechanism.
        Templates can also express attributes on objects, such as network.id;
        templates can also be nested, thus allowing for iteration on inner
        templates.

        Examples:
        1) template with class attributes
        Name: %(person.name)s \n
        Surname: %(person.surname)s \n
        2) template with iteration
        Telephone numbers: \n
        %(phone_numbers|Telephone number:%(number)s)
        3) template with iteration and class attributes
        Addresses: \n
        %(Addresses|Street:%(address.street)s\nNumber%(address.number))

        Instances of this class are initialized with a template string and
        the dictionary for performing substition. The class implements the
        __str__ method, so it can be directly printed.
    """

    def __init__(self, template, data):
        self._template = template
        self.data = data

    def __str__(self):
        return self._template % self

    def __getitem__(self, key):
        items = key.split("|")
        if len(items) == 1:
            return self._make_attribute(key)
        else:
            # Note(salvatore-orlando): items[0] must be subscriptable
            return self._make_list(self.data[items[0]], items[1])

    def _make_attribute(self, item):
        """ Renders an entity attribute key in the template.
           e.g.: entity.attribute
        """
        items = item.split('.')
        if len(items) == 1:
            return self.data[item]
        elif len(items) == 2:
            return self.data[items[0]][items[1]]

    def _make_list(self, items, inner_template):
        """ Renders a list key in the template.
            e.g.: %(list|item data:%(item))
        """
        #make sure list is subscriptable
        if not hasattr(items, '__getitem__'):
            raise Exception("Element is not iterable")
        return "\n".join([inner_template % item for item in items])


class CmdOutputTemplate(OutputTemplate):
    """ This class provides templated output for CLI commands.
        Extends OutputTemplate loading a different template for each command.
    """

    _templates = {
        "list_subnets":   "Subnets for Tenant %(tenant_id)s\n" +
                          "%(subnets|\tSubnet ID: %(id)s)s",
        "show_subnet":    "Subnet ID: %(subnet.id)s\n" +
                          "CIDR: %(subnet.cidr)s\n" +
                          "Network ID: %(subnet.network_id)s",
        "create_subnet":     "Created a new Subnet with ID: " +
                          "%(subnet_id)s\n" +
                          "for Tenant: %(tenant_id)s",
        "update_subnet":     "Updated Subnet with ID: %(subnet_id)s\n" +
                          "for Tenant: %(tenant_id)s\n",
        "delete_subnet":     "Deleted Subnet with ID: %(subnet_id)s\n" +
                          "for Tenant %(tenant_id)s",
        "list_routetables":   "Routetables for Tenant %(tenant_id)s\n" +
                          "%(routetables|\tRoutetable ID: %(id)s)s",
        "show_routetable":    "Routetable ID: %(routetable.id)s\n" +
                          "label: %(routetable.label)s\n" +
                          "description: %(routetable.description)s",
        "create_routetable":     "Created a new Routetable with ID: " +
                          "%(routetable_id)s\n" +
                          "for Tenant: %(tenant_id)s",
        "update_routetable":     "Updated Routetable with ID: %(routetable_id)s\n" +
                          "for Tenant: %(tenant_id)s\n",
        "delete_routetable":     "Deleted Routetable with ID: %(routetable_id)s\n" +
                          "for Tenant %(tenant_id)s",
        "list_routes":   "Routes for Tenant: %(tenant_id)s " + 
                         "Routetable ID: %(routetable_id)s\n" + 
                         "\tRoute-ID\tSource\tDestination\tTarget\n" +
                         "%(routes|\t%(id)s\t" +
                         "%(source)s\t" +
                         "%(destination)s\t" +
                         "%(target)s)s",
        "create_route":   "Created a new Route ID %(id)s with\n" +
                          "Source: %(source)s\n" +
                          "Destination: %(destination)s\n" +
                          "Target: %(target)s\n" +
                          "in Routetable: %(routetable_id)s\n" +
                          "for Tenant: %(tenant_id)s",
        "delete_route": "Deleted Route: %(id)s\n" +
                         "from Routetable: %(routetable_id)s\n" +
                         "for Tenant: %(tenant_id)s",
        "update_route": "Updated Route ID: %(id)s \n" +
                        "in Routetable: %(routetable_id)s\n" +
                        "for Tenant: %(tenant_id)s\n",
        "show_route":   "Route-ID: %(route.id)s\n" +
                        "Routetable: %(route.routetable_id)s\n" +
                        "Source: %(route.source)s\n" +
                        "Destination: %(route.destination)s\n" +
                        "Target: %(route.target)s",
        "list_available_targets": "Targets for Tenant: %(tenant_id)s\n" + 
                         "\tTarget-ID\tDescription\n" +
                         "%(targets|\t%(tag)s\t" +
                         "%(description)s)s",
        "show_subnet_association": "Subnet ID: %(subnet_id)s is associated with " +
                          "Route-table: %(association.routetable_id)s",
        "associate_subnet": "Associated Subnet ID: %(subnet_id)s with " +
                          "Route-table: %(routetable_id)s",
        "disassociate_subnet": "Removed association of Subnet ID: " +
                          "%(subnet_id)s with " +
                          "Route-table: %(association.routetable_id)s",
        }

    def __init__(self, cmd, data):
        super(CmdOutputTemplate, self).__init__(self._templates[cmd], data)


def _handle_exception(ex):
    LOG.exception(sys.exc_info())
    print "Exception:%s - %s" % (sys.exc_info()[0], sys.exc_info()[1])
    status_code = None
    message = None
    # Retrieve dict at 1st element of tuple at last argument
    if ex.args and isinstance(ex.args[-1][0], dict):
        status_code = ex.args[-1][0].get('status_code', None)
        message = ex.args[-1][0].get('message', None)
        msg_1 = "Command failed with error code: %s" \
                % (status_code or '<missing>')
        msg_2 = "Error message:%s" % (message or '<missing>')
        LOG.exception(msg_1 + "-" + msg_2)
        print msg_1
        print msg_2


def prepare_output(cmd, tenant_id, response):
    LOG.debug("Preparing output for response:%s", response)
    response['tenant_id'] = tenant_id
    output = str(CmdOutputTemplate(cmd, response))
    LOG.debug("Finished preparing output for command:%s", cmd)
    return output


def list_subnets(client, *args):
    tenant_id = args[0]
    res = client.list_subnets()
    LOG.debug("Operation 'list_subnets' executed.")
    output = prepare_output("list_subnets", tenant_id, res)
    print output


def create_subnet(client, *args):
    tenant_id, cidr = args
    data = {'subnet': {'cidr': cidr}}
    new_subnet_id = None
    try:
        res = client.create_subnet(data)
        new_subnet_id = res["subnet"]["id"]
        LOG.debug("Operation 'create_subnet' executed.")
        output = prepare_output("create_subnet", tenant_id,
                                          dict(subnet_id=new_subnet_id))
        print output
    except Exception as ex:
        _handle_exception(ex)


def delete_subnet(client, *args):
    tenant_id, subnet_id = args
    try:
        client.delete_subnet(subnet_id)
        LOG.debug("Operation 'delete_subnet' executed.")
        output = prepare_output("delete_subnet", tenant_id,
                            dict(subnet_id=subnet_id))
        print output
    except Exception as ex:
        _handle_exception(ex)


def show_subnet(client, *args):
    tenant_id, subnet_id = args
    try:
        res = client.show_subnet_details(subnet_id)["subnet"]
        LOG.debug("Operation 'show_subnet_details' executed.")
        output = prepare_output("show_subnet", tenant_id,
                                          dict(subnet=res))
        print output
    except Exception as ex:
        _handle_exception(ex)


def update_subnet(client, *args):
    tenant_id, subnet_id, param_data = args
    data = {'subnet': {}}
    for kv in param_data.split(","):
        k, v = kv.split("=")
        data['subnet'][k] = v
    data['subnet']['id'] = subnet_id
    try:
        client.update_subnet(subnet_id, data)
        LOG.debug("Operation 'update_subnet' executed.")
        # Response has no body. Use data for populating output
        output = prepare_output("update_subnet", tenant_id, data)
        print output
    except Exception as ex:
        _handle_exception(ex)


def list_routetables(client, *args):
    tenant_id = args[0]
    res = client.list_routetables()
    LOG.debug("Operation 'list_routetables' executed.")
    output = prepare_output("list_routetables", tenant_id, res)
    print output


def create_routetable(client, *args):
    tenant_id = args
    try:
        res = client.create_routetable()
        routetable_id = res["routetable"]["id"]
        LOG.debug("Operation 'create_routetable' executed.")
        output = prepare_output("create_routetable", tenant_id,
                                dict(routetable_id=routetable_id))
        print output
    except Exception as ex:
        _handle_exception(ex)


def delete_routetable(client, *args):
    tenant_id, routetable_id = args
    try:
        client.delete_routetable(routetable_id)
        LOG.debug("Operation 'delete_routetable' executed.")
        output = prepare_output("delete_routetable", tenant_id,
                            dict(routetable_id=routetable_id))
        print output
    except Exception as ex:
        _handle_exception(ex)


def show_routetable(client, *args):
    tenant_id, routetable_id = args
    try:
        res = client.show_routetable_details(routetable_id)["routetable"]
        LOG.debug("Operation 'show_routetable_details' executed.")
        output = prepare_output("show_routetable", tenant_id,
                                          dict(routetable=res))
        print output
    except Exception as ex:
        _handle_exception(ex)


def update_routetable(client, *args):
    tenant_id, routetable_id, param_data = args
    data = {'routetable': {}}
    for kv in param_data.split(","):
        k, v = kv.split("=")
        data['routetable'][k] = v
    data['routetable']['id'] = routetable_id
    try:
        client.update_routetable(routetable_id, data)
        LOG.debug("Operation 'update_routetable' executed.")
        # Response has no body. Use data for populating output
        output = prepare_output("update_routetable", tenant_id, data)
        print output
    except Exception as ex:
        _handle_exception(ex)


def list_routes(client, *args):
    tenant_id, routetable_id = args
    try:
        res = client.list_routes(routetable_id)
        LOG.debug("Operation 'list_routes' executed.")
        data = res
        data['routetable_id'] = routetable_id
        output = prepare_output("list_routes", tenant_id, data)
        print output
    except Exception as ex:
        _handle_exception(ex)


def create_route(client, *args):
    tenant_id, routetable_id, source, destination, target = args
    data = {'route': {'source': source,
                      'destination': destination,
                      'target': target}}
    try:
        res = client.create_route(routetable_id, data)
        res_route_id = res["route"]["id"]
        res_routetable_id = res["route"]["routetable_id"]
        res_source = res["route"]["source"]
        res_destination = res["route"]["destination"]
        res_target = res["route"]["target"]
        LOG.debug("Operation 'create_route' executed.")
        output = prepare_output("create_route", tenant_id,
                                          dict(id=res_route_id,
                                               routetable_id=res_routetable_id,
                                               source=res_source,
                                               destination=res_destination,
                                               target=res_target))
        print output
    except Exception as ex:
        _handle_exception(ex)


def delete_route(client, *args):
    tenant_id, routetable_id, route_id = args
    try:
        client.delete_route(routetable_id, route_id)
        LOG.debug("Operation 'delete_route' executed.")
        output = prepare_output("delete_route", tenant_id,
                            dict(routetable_id=routetable_id,
                                 id=route_id))
        print output
    except Exception as ex:
        _handle_exception(ex)


def show_route(client, *args):
    tenant_id, routetable_id, route_id = args
    try:
        res = client.show_route_details(routetable_id, route_id)["route"]
        LOG.debug("Operation 'show_route_details' executed.")
        output = prepare_output("show_route", tenant_id,
                                          dict(route=res))
        print output
    except Exception as ex:
        _handle_exception(ex)


def update_route(client, *args):
    tenant_id, routetable_id, route_id, param_data = args
    data = {'route': {}}
    for kv in param_data.split(","):
        k, v = kv.split("=")
        data['route'][k] = v
    data['routetable_id'] = routetable_id
    data['route']['id'] = route_id
    try:
        client.update_route(routetable_id, route_id, data)
        LOG.debug("Operation 'update_route' executed.")
        # Response has no body. Use data for populating output
        output = prepare_output("update_route", tenant_id, data)
        print output
    except Exception as ex:
        _handle_exception(ex)


def list_available_targets(client, *args):
    tenant_id, routetable_id = args
    try:
        result = client.list_available_targets(routetable_id)
        LOG.debug("Operation 'list_available_targets' executed.")
        output = prepare_output("list_available_targets", tenant_id, result)
        print output
    except Exception as ex:
        _handle_exception(ex)


def show_subnet_association(client, *args):
    tenant_id, subnet_id = args
    try:
        res = client.show_subnet_association(subnet_id)["association"]
        LOG.debug("Operation 'show_subnet_association' executed", res)
        if not res:
            res = {"routetable_id": None}
        output = prepare_output("show_subnet_association", tenant_id,
                                dict(association=res, subnet_id=subnet_id))
        print output
    except Exception as ex:
        _handle_exception(ex)


def associate_subnet(client, *args):
    tenant_id, subnet_id, routetable_id = args
    try:
        data = {'association': {'routetable_id': '%s' % routetable_id}}
        client.associate_subnet(subnet_id, data)
        LOG.debug("Operation 'associate_subnet' executed.")
        output = prepare_output("associate_subnet", tenant_id,
                                dict(subnet_id=subnet_id,
                                     routetable_id=routetable_id))
        print output
    except Exception as ex:
        _handle_exception(ex)


def disassociate_subnet(client, *args):
    tenant_id, subnet_id = args
    try:
        res = client.disassociate_subnet(subnet_id)["association"]
        LOG.debug("Operation 'disassociate_subnet' executed.")
        output = prepare_output("disassociate_subnet", tenant_id,
                                dict(association=res,
                                     subnet_id=subnet_id))
        print output
    except Exception as ex:
        _handle_exception(ex)
