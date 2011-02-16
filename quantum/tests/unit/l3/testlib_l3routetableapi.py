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

import webob

from quantum.common.serializer import Serializer


def create_request(path, body, content_type, method='GET'):
    req = webob.Request.blank(path)
    req.method = method
    req.headers = {}
    req.headers['Accept'] = content_type
    req.body = body
    return req


def _routetable_list_request(tenant_id, format='xml', detail=False):
    method = 'GET'
    detail_str = detail and '/detail' or ''
    path = "/tenants/%(tenant_id)s/routetables" \
           "%(detail_str)s.%(format)s" % locals()
#    ".%(format)s" % locals()
    content_type = "application/%s" % format
    return create_request(path, None, content_type, method)


def routetable_list_request(tenant_id, format='xml'):
    return _routetable_list_request(tenant_id, format)


def routetable_list_detail_request(tenant_id, format='xml'):
    return _routetable_list_request(tenant_id, format, detail=True)


def _show_routetable_request(tenant_id, routetable_id, 
							 format='xml', detail=False):
    method = 'GET'
    detail_str = detail and '/detail' or ''
    path = "/tenants/%(tenant_id)s/routetables" \
           "/%(routetable_id)s%(detail_str)s.%(format)s" % locals()
    content_type = "application/%s" % format
    return create_request(path, None, content_type, method)


def show_routetable_request(tenant_id, routetable_id, format='xml'):
    return _show_routetable_request(tenant_id, routetable_id, format)


def show_routetable_detail_request(tenant_id, routetable_id, format='xml'):
    return _show_routetable_request(tenant_id, routetable_id, format, detail=True)


def new_routetable_request(tenant_id, format='xml', custom_req_body=None):
    label='label'
    method = 'POST'
    path = "/tenants/%(tenant_id)s/routetables.%(format)s" % locals()
    body = custom_req_body or {'routetable': {}}
    content_type = "application/%s" % format
    if body != None :
		body = Serializer().serialize(body, content_type)
    return create_request(path, body, content_type, method)


def update_routetable_request(tenant_id, routetable_id, cidr, format='xml',
                           custom_req_body=None):
    method = 'PUT'
    path = "/tenants/%(tenant_id)s/routetables" \
           "/%(routetable_id)s.%(format)s" % locals()
    data = custom_req_body or {'routetable':{'label': '%s' % label} }
    content_type = "application/%s" % format
    body = Serializer().serialize(data, content_type)
    return create_request(path, body, content_type, method)


def routetable_delete_request(tenant_id, routetable_id, format='xml'):
    method = 'DELETE'
    path = "/tenants/%(tenant_id)s/routetables/" \
           "%(routetable_id)s.%(format)s" % locals()
    content_type = "application/%s" % format
    return create_request(path, None, content_type, method)
