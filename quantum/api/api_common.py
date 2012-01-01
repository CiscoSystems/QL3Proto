# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 Citrix System.
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

import logging

from webob import exc

from quantum import wsgi
from quantum.api import faults

XML_NS_V10 = 'http://openstack.org/quantum/api/v1.0'
XML_NS_V11 = 'http://openstack.org/quantum/api/v1.1'
LOG = logging.getLogger('quantum.api.api_common')


class OperationalStatus:
    """ Enumeration for operational status

        UP : the resource is available (operationall up)
        DOWN : the resource is not operational; this might indicate
               a failure in the underlying switching fabric.
        PROVISIONING: the plugin is creating or updating the resource
                      in the underlying switching fabric
        UNKNOWN: the plugin does not support the operational status concept.
    """
    UP = "UP"
    DOWN = "DOWN"
    PROVISIONING = "PROVISIONING"
    UNKNOWN = "UNKNOWN"


def create_resource(version, controller_dict):
    """
    Generic function for creating a wsgi resource
    The function takes as input:
     - desired version
     - controller and metadata dictionary
       e.g.: {'1.0': [ctrl_v10, meta_v10, xml_ns],
              '1.1': [ctrl_v11, meta_v11, xml_ns]}

    """
    # the first element of the iterable is expected to be the controller
    controller = controller_dict[version][0]
    # the second element should be the metadata
    metadata = controller_dict[version][1]
    # and the third element the xml namespace
    xmlns = controller_dict[version][2]

    headers_serializer = HeaderSerializer()
    xml_serializer = wsgi.XMLDictSerializer(metadata, xmlns)
    json_serializer = wsgi.JSONDictSerializer()
    xml_deserializer = wsgi.XMLDeserializer(metadata)
    json_deserializer = wsgi.JSONDeserializer()

    body_serializers = {
        'application/xml': xml_serializer,
        'application/json': json_serializer,
    }

    body_deserializers = {
        'application/xml': xml_deserializer,
        'application/json': json_deserializer,
    }

    serializer = wsgi.ResponseSerializer(body_serializers, headers_serializer)
    deserializer = wsgi.RequestDeserializer(body_deserializers)

    return wsgi.Resource(controller, deserializer, serializer)


def APIFaultWrapper(errors=None):

    def wrapper(func, **kwargs):

        def the_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if errors != None and type(e) in errors:
                    raise faults.QuantumHTTPError(e)
                # otherwise just re-raise
                raise
        the_func.__name__ = func.__name__
        return the_func

    return wrapper


class HeaderSerializer(wsgi.ResponseHeaderSerializer):
    """
    Defines default respone status codes for Quantum API operations
        create - 202 ACCEPTED
        update - 204 NOCONTENT
        delete - 204 NOCONTENT
        others - 200 OK (defined in base class)

    """

    def create(self, response, data):
        response.status_int = 202

    def delete(self, response, data):
        response.status_int = 204

    def update(self, response, data):
        response.status_int = 204

    def attach_resource(self, response, data):
        response.status_int = 204

    def detach_resource(self, response, data):
        response.status_int = 204


class QuantumController(object):
    """ Base controller class for Quantum API """

    def __init__(self, plugin):
        self._plugin = plugin
        super(QuantumController, self).__init__()

    def _prepare_request_body(self, body, params):
        """ verifies required parameters are in request body.
            sets default value for missing optional parameters.

            body argument must be the deserialized body
        """
        try:
            if body is None:
                # Initialize empty resource for setting default value
                body = {self._resource_name: {}}
            data = body[self._resource_name]
        except KeyError:
            # raise if _resource_name is not in req body.
            raise exc.HTTPBadRequest("Unable to find '%s' in request body"\
                                     % self._resource_name)
        for param in params:
            param_name = param['param-name']
            param_value = data.get(param_name, None)
            # If the parameter wasn't found and it was required, return 400
            if param_value is None and param['required']:
                msg = ("Failed to parse request. " +
                       "Parameter: " + param_name + " not specified")
                for line in msg.split('\n'):
                    LOG.error(line)
                raise exc.HTTPBadRequest(msg)
            data[param_name] = param_value or param.get('default-value')
        return body
