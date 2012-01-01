# vim: tabstop=4 shiftwidth=4 softtabstop=4

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
#    @author: Sumit Naiksatam, Cisco Systems

import logging
import httplib
import socket
import urllib

from quantum.common import exceptions
from quantum.common.serializer import Serializer

LOG = logging.getLogger('quantum.client')
EXCEPTIONS = {
    400: exceptions.BadInputError,
    401: exceptions.NotAuthorized,
    450: exceptions.SubnetNotFound,
    451: exceptions.InvalidCIDR,
    452: exceptions.DuplicateCIDR,
    453: exceptions.SubnetAlreadyAssociated,
    460: exceptions.RoutetableNotFound,
    465: exceptions.RouteNotFound,
    466: exceptions.RouteSourceInvalid,
    467: exceptions.RouteDestinationInvalid,
    468: exceptions.RouteTargetInvalid}

AUTH_TOKEN_HEADER = "X-Auth-Token"


class ApiCall(object):
    """A Decorator to add support for format and tenant overriding"""
    def __init__(self, function):
        self.function = function

    def __get__(self, instance, owner):
        def with_params(*args, **kwargs):
            """
            Temporarily sets the format and tenant for this request
            """
            (format, tenant) = (instance.format, instance.tenant)

            if 'format' in kwargs:
                instance.format = kwargs['format']
            if 'tenant' in kwargs:
                instance.tenant = kwargs['tenant']

            ret = self.function(instance, *args)
            (instance.format, instance.tenant) = (format, tenant)
            return ret
        return with_params


class Client(object):

    """A base client class - derived from Glance.BaseClient"""

    #Metadata for deserializing xml
    _serialization_metadata = {
        "application/xml": {
            "attributes": {
                "subnet": ["id", "cidr", "network_id"],
                "association": ["routetable_id"],
                "routetable": ["id", "label", "description"],
                "route": ["id", "source", "destination", "target"],
                "target": ["tag", "description"]},
            "plurals": {"subnets": "subnet",
                        "routetables": "routetable",
                        "routes": "route",
                        "targets": "target"}},
    }

    # Action query strings
    subnets_path = "/subnets"
    subnet_path = "/subnets/%s"
    routetables_path = "/routetables"
    routetable_path = "/routetables/%s"
    routes_path = "/routetables/%s/routes"
    route_path = "/routetables/%s/routes/%s"
    targets_path = "/routetables/%s/targets"
    association_path = "/subnets/%s/association"

    def __init__(self, host="127.0.0.1", port=9696, use_ssl=False, tenant=None,
                format="xml", testingStub=None, key_file=None, cert_file=None,
                auth_token=None, logger=None,
                action_prefix="/v1.1/tenants/{tenant_id}"):
        """
        Creates a new client to some service.

        :param host: The host where service resides
        :param port: The port where service resides
        :param use_ssl: True to use SSL, False to use HTTP
        :param tenant: The tenant ID to make requests with
        :param format: The format to query the server with
        :param testingStub: A class that stubs basic server methods for tests
        :param key_file: The SSL key file to use if use_ssl is true
        :param cert_file: The SSL cert file to use if use_ssl is true
        :param auth_token: authentication token to be passed to server
        :param logger: Logger object for the client library
        :param action_prefix: prefix for request URIs
        """
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.tenant = tenant
        self.format = format
        self.connection = None
        self.testingStub = testingStub
        self.key_file = key_file
        self.cert_file = cert_file
        self.logger = logger
        self.auth_token = auth_token
        self.action_prefix = action_prefix

    def get_connection_type(self):
        """
        Returns the proper connection type
        """
        if self.testingStub:
            return self.testingStub
        if self.use_ssl:
            return httplib.HTTPSConnection
        else:
            return httplib.HTTPConnection

    def _send_request(self, conn, method, action, body, headers):
        if self.logger:
            self.logger.debug("Quantum Client Request:\n" \
                    + method + " " + action + "\n")
            if body:
                self.logger.debug(body)
        conn.request(method, action, body, headers)
        return conn.getresponse()

    def do_request(self, method, action, body=None,
                   headers=None, params=None, exception_args={}):
        """
        Connects to the server and issues a request.
        Returns the result data, or raises an appropriate exception if
        HTTP status code is not 2xx

        :param method: HTTP method ("GET", "POST", "PUT", etc...)
        :param body: string of data to send, or None (default)
        :param headers: mapping of key/value pairs to add as headers
        :param params: dictionary of key/value pairs to add to append
                             to action

        """
        LOG.debug("Client issuing request: %s", action)
        # Ensure we have a tenant id
        if not self.tenant:
            raise Exception("Tenant ID not set")

        # Add format and tenant_id
        action += ".%s" % self.format
        action = self.action_prefix + action
        action = action.replace('{tenant_id}', self.tenant)

        if type(params) is dict:
            action += '?' + urllib.urlencode(params)
        if body:
            body = self.serialize(body)

        try:
            connection_type = self.get_connection_type()
            headers = headers or {"Content-Type":
                                      "application/%s" % self.format}
            # if available, add authentication token
            if self.auth_token:
                headers[AUTH_TOKEN_HEADER] = self.auth_token
            # Open connection and send request, handling SSL certs
            certs = {'key_file': self.key_file, 'cert_file': self.cert_file}
            certs = dict((x, certs[x]) for x in certs if certs[x] != None)

            if self.use_ssl and len(certs):
                conn = connection_type(self.host, self.port, **certs)
            else:
                conn = connection_type(self.host, self.port)
            res = self._send_request(conn, method, action, body, headers)
            status_code = self.get_status_code(res)
            data = res.read()

            if self.logger:
                self.logger.debug("Quantum Client Reply (code = %s) :\n %s" \
                        % (str(status_code), data))
            if status_code in (httplib.OK,
                               httplib.CREATED,
                               httplib.ACCEPTED,
                               httplib.NO_CONTENT):
                return self.deserialize(data, status_code)
            else:
                error_message = res.read()
                LOG.debug("Server returned error: %s", status_code)
                LOG.debug("Error message: %s", error_message)
                # Create exception with HTTP status code and message
                if res.status in EXCEPTIONS:
                    raise EXCEPTIONS[res.status](**exception_args)
                # Add error code and message to exception arguments
                ex = Exception("Server returned error: %s" % status_code)
                ex.args = ([dict(status_code=status_code,
                                 message=error_message)],)
                raise ex
        except (socket.error, IOError), e:
            msg = "Unable to connect to server. Got error: %s" % e
            LOG.exception(msg)
            raise Exception(msg)

    def get_status_code(self, response):
        """
        Returns the integer status code from the response, which
        can be either a Webob.Response (used in testing) or httplib.Response
        """
        if hasattr(response, 'status_int'):
            return response.status_int
        else:
            return response.status

    def serialize(self, data):
        """
        Serializes a dictionary with a single key (which can contain any
        structure) into either xml or json
        """
        if data is None:
            return None
        elif type(data) is dict:
            return Serializer().serialize(data, self.content_type())
        else:
            raise Exception("unable to serialize object of type = '%s'" \
                                % type(data))

    def deserialize(self, data, status_code):
        """
        Deserializes a an xml or json string into a dictionary
        """
        if status_code == 204:
            return data
        return Serializer(self._serialization_metadata).\
                    deserialize(data, self.content_type())

    def content_type(self, format=None):
        """
        Returns the mime-type for either 'xml' or 'json'.  Defaults to the
        currently set format
        """
        if not format:
            format = self.format
        return "application/%s" % (format)

    @ApiCall
    def list_subnets(self):
        """
        Fetches a list of all subnets for a tenant
        """
        return self.do_request("GET", self.subnets_path)

    @ApiCall
    def show_subnet_details(self, subnet):
        """
        Fetches the details of a certain subnet
        """
        return self.do_request("GET", self.subnet_path % (subnet),
                                        exception_args={"subnet_id": subnet})

    @ApiCall
    def create_subnet(self, body=None):
        """
        Creates a new subnet
        """
        return self.do_request("POST", self.subnets_path, body=body)

    @ApiCall
    def update_subnet(self, subnet, body=None):
        """
        Updates a subnet
        """
        return self.do_request("PUT", self.subnet_path % (subnet), body=body,
                                        exception_args={"subnet_id": subnet})

    @ApiCall
    def delete_subnet(self, subnet):
        """
        Deletes the specified subnet
        """
        return self.do_request("DELETE", self.subnet_path % (subnet),
                                        exception_args={"subnet_id": subnet})

    @ApiCall
    def list_routetables(self):
        """
        Fetches a list of all routetables for a tenant
        """
        return self.do_request("GET", self.routetables_path)

    @ApiCall
    def show_routetable_details(self, routetable):
        """
        Fetches the details of a certain routetable
        """
        return self.do_request("GET", self.routetable_path % (routetable),
                                exception_args={"routetable_id": routetable})

    @ApiCall
    def create_routetable(self, body=None):
        """
        Creates a new routetable
        """
        return self.do_request("POST", self.routetables_path, body=body)

    @ApiCall
    def update_routetable(self, routetable, body=None):
        """
        Updates a routetable
        """
        return self.do_request("PUT", self.routetable_path % (routetable),
                               body=body,
                               exception_args={"routetable_id": routetable})

    @ApiCall
    def delete_routetable(self, routetable):
        """
        Deletes the specified routetable
        """
        return self.do_request("DELETE", self.routetable_path % (routetable),
                               exception_args={"routetable_id": routetable})

    @ApiCall
    def list_routes(self, routetable):
        """
        Fetches a list of all routes for a tenant
        """
        return self.do_request("GET", self.routes_path % routetable)

    @ApiCall
    def create_route(self, routetable, body=None):
        """
        Creates a new route
        """
        return self.do_request("POST", self.routes_path % routetable,
                               body=body)

    @ApiCall
    def delete_route(self, routetable, route, body=None):
        """
        Deletes the specified route
        """
        return self.do_request("DELETE",
                               self.route_path % (routetable, route),
                               exception_args={"route_id": route,
                                               "routetable_id": routetable})

    @ApiCall
    def show_route_details(self, routetable, route):
        """
        Fetches the details of a certain route
        """
        return self.do_request("GET", self.route_path % (routetable, route),
                               exception_args={"route_id": route,
                                               "routetable_id": routetable})

    @ApiCall
    def update_route(self, routetable, route, body=None):
        """
        Updates a route
        """
        return self.do_request("PUT", self.route_path % (routetable, route),
                               body=body, exception_args={"route_id": route,
                                               "routetable_id": routetable})

    @ApiCall
    def list_available_targets(self, routetable):
        """
        Fetches a list of all available targets for a tenant
        """
        return self.do_request("GET", self.targets_path % routetable)

    @ApiCall
    def show_subnet_association(self, subnet):
        """
        Fetches the routetable associated with a subnet
        """
        return self.do_request("GET", self.association_path % (subnet),
                                        exception_args={"subnet_id": subnet})

    @ApiCall
    def associate_subnet(self, subnet, body=None):
        """
        Associates a subnet with a routetable
        """
        return self.do_request("PUT",
            self.association_path % (subnet), body=body,
                       exception_args={"subnet_id": subnet,
                                       "routetable_id": str(body)})

    @ApiCall
    def disassociate_subnet(self, subnet):
        """
        Removes the asssociation of the subnet with the routetable
        """
        return self.do_request("DELETE",
                               self.association_path % (subnet),
                    exception_args={"subnet_id": subnet})
