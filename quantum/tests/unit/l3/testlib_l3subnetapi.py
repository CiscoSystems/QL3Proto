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
    """Return complete request"""
    req = webob.Request.blank(path)
    req.method = method
    req.headers = {}
    req.headers['Accept'] = content_type
    req.body = body
    return req


def _subnet_list_request(tenant_id, format='xml', detail=False):
    """Return request for list_subnets"""
    method = 'GET'
    detail_str = detail and '/detail' or ''
    path = "/tenants/%(tenant_id)s/subnets" \
           "%(detail_str)s.%(format)s" % locals()
    content_type = "application/%s" % format
    return create_request(path, None, content_type, method)


def subnet_list_request(tenant_id, format='xml'):
    """Make request for subnet_list"""
    return _subnet_list_request(tenant_id, format)


def subnet_list_detail_request(tenant_id, format='xml'):
    """Make request for subnet_list with detail"""
    return _subnet_list_request(tenant_id, format, detail=True)


def _show_subnet_request(tenant_id, subnet_id, format='xml', detail=False):
    """Return request for show_subnet"""
    method = 'GET'
    detail_str = detail and '/detail' or ''
    path = "/tenants/%(tenant_id)s/subnets" \
           "/%(subnet_id)s%(detail_str)s.%(format)s" % locals()
    content_type = "application/%s" % format
    return create_request(path, None, content_type, method)


def show_subnet_request(tenant_id, subnet_id, format='xml'):
    """Make request for show_subnet"""
    return _show_subnet_request(tenant_id, subnet_id, format)


def show_subnet_detail_request(tenant_id, subnet_id, format='xml'):
    """Make request for show_subnet with detail"""
    return _show_subnet_request(tenant_id, subnet_id, format, detail=True)


def new_subnet_request(tenant_id, cidr='10.0.0.0/16',
                        format='xml', custom_req_body=None):
    """Return request for create_subnet"""
    method = 'POST'
    path = "/tenants/%(tenant_id)s/subnets.%(format)s" % locals()
    data = custom_req_body or {'subnet': {'cidr': '%s' % cidr}}
    content_type = "application/%s" % format
    body = Serializer().serialize(data, content_type)
    return create_request(path, body, content_type, method)


def update_subnet_request(tenant_id, subnet_id, cidr, format='xml',
                           custom_req_body=None):
    """Make request for update_subnet"""
    method = 'PUT'
    path = "/tenants/%(tenant_id)s/subnets" \
           "/%(subnet_id)s.%(format)s" % locals()
    data = custom_req_body or {'subnet': {'cidr': '%s' % cidr}}
    content_type = "application/%s" % format
    body = Serializer().serialize(data, content_type)
    return create_request(path, body, content_type, method)


def subnet_delete_request(tenant_id, subnet_id, format='xml'):
    """Make request for subnet_delete"""
    method = 'DELETE'
    path = "/tenants/%(tenant_id)s/subnets/" \
           "%(subnet_id)s.%(format)s" % locals()
    content_type = "application/%s" % format
    return create_request(path, None, content_type, method)
