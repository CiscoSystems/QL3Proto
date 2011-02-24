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
#    @author: Shubhangi Satras, Cisco Systems, Inc.
""" Test Library file for Routetable """
import logging as LOG
import webob

from quantum.common.serializer import Serializer


def create_request(path, body, content_type, method='GET'):
    """Creation of Request """
    req = webob.Request.blank(path)
    req.method = method
    req.headers = {}
    req.headers['Accept'] = content_type
    req.body = body
    return req


def _routetable_list_request(tenant_id, req_format, detail=False):
    """Request for listing routetable"""
    method = 'GET'
    detail_str = detail and '/detail' or ''
    LOG.debug("detail_str: %s , tenant_id: %s",
               detail_str, tenant_id)
    path = "/tenants/%(tenant_id)s/routetables" \
           "%(detail_str)s.%(req_format)s" % locals()
#    ".%(req_format)s" % locals()
    content_type = "application/%s" % req_format
    return create_request(path, None, content_type, method)


def routetable_list_request(tenant_id, req_format):
    """Request for listing routetable"""
    return _routetable_list_request(tenant_id, req_format)


def routetable_list_detail_request(tenant_id, req_format):
    """Request for listing routetable with each entry in detail"""
    return _routetable_list_request(tenant_id, req_format, detail=True)


def _show_routetable_request(tenant_id, routetable_id,
                             req_format, detail=False):
    """Request to show routetable"""
    method = 'GET'
    detail_str = detail and '/detail' or ''
    LOG.debug("detail_str: %s , tenant_id: %s, routetable_id: %s ",
               detail_str, tenant_id, routetable_id)
    path = "/tenants/%(tenant_id)s/routetables" \
           "/%(routetable_id)s%(detail_str)s.%(req_format)s" % locals()
    content_type = "application/%s" % req_format
    return create_request(path, None, content_type, method)


def show_routetable_request(tenant_id, routetable_id, req_format):
    """Request to show routetable"""
    return _show_routetable_request(tenant_id, routetable_id, req_format)


def show_routetable_detail_request(tenant_id, routetable_id, req_format):
    """Request to show routetable in detail"""
    return _show_routetable_request(tenant_id, routetable_id,
                                    req_format, detail=True)


def new_routetable_request(tenant_id, req_format, custom_req_body=None):
    """Request to create new routetable"""
    method = 'POST'
    LOG.debug("tenant_id: %s", tenant_id)
    path = "/tenants/%(tenant_id)s/routetables.%(req_format)s" % locals()
    body = custom_req_body or {'routetable': {}}
    content_type = "application/%s" % req_format
    if body != None:
        body = Serializer().serialize(body, content_type)
    return create_request(path, body, content_type, method)


def update_routetable_request(tenant_id, routetable_id, label, req_format,
                           custom_req_body=None):
    """Request to update routetable"""
    method = 'PUT'
    LOG.debug("tenant_id: %s, routetable_id: %s ",
               tenant_id, routetable_id)
    path = "/tenants/%(tenant_id)s/routetables" \
           "/%(routetable_id)s.%(req_format)s" % locals()
    data = custom_req_body or {'routetable': {'label': '%s' % label}}
    content_type = "application/%s" % req_format
    body = Serializer().serialize(data, content_type)
    return create_request(path, body, content_type, method)


def routetable_delete_request(tenant_id, routetable_id, req_format):
    """Request to delete routetable"""
    method = 'DELETE'
    path = "/tenants/%(tenant_id)s/routetables/" \
           "%(routetable_id)s.%(req_format)s" % locals()
    LOG.debug("tenant_id: %s, routetable_id: %s ",
               tenant_id, routetable_id)
    content_type = "application/%s" % req_format
    return create_request(path, None, content_type, method)
