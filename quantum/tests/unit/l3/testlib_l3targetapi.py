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
#    @author: Atul Gaikwad, Cisco Systems, Inc.
"""Testlib for L3 Target API tests"""

import webob

from quantum.common.serializer import Serializer


def create_request(path, body, content_type, method='GET'):
    """creating request"""
    req = webob.Request.blank(path)
    req.method = method
    req.headers = {}
    req.headers['Accept'] = content_type
    req.body = body
    return req


def _target_list_request(tenant_id, routetable_id, req_format='xml'):
    """creting request for target list"""
    method = 'GET'
    path = "/tenants/" + str(tenant_id) + "/routetables/" +\
            str(routetable_id) + "/targets.%(req_format)s" % locals()
    content_type = "application/%s" % req_format
    return create_request(path, None, content_type, method)


def target_list_request(tenant_id, routetable_id, req_format='xml'):
    """creting request for target list"""
    return _target_list_request(tenant_id, routetable_id, req_format)


def new_routetable_request(tenant_id, req_format='xml', custom_req_body=None):
    """creting request for a new routetable"""
    label = 'label'
    method = 'POST'
    path = "/tenants/" + str(tenant_id) +\
           "/routetables.%(req_format)s" % locals()
    data = custom_req_body or {'routetable': {'label': '%s' % label}}
    content_type = "application/%s" % req_format
    body = Serializer().serialize(data, content_type)
    return create_request(path, body, content_type, method)
