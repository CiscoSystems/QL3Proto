# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011, Cisco Systems, Inc.
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
# @author: Rohit Agarwalla, Cisco Systems, Inc.

from sqlalchemy.orm import exc

from quantum.db.api import *
from quantum.plugins.l3 import plugin_configuration as conf

import logging as LOG


def initialize():
    'Establish database connection and load models'
    options = {"sql_connection": "mysql://%s:%s@%s/%s" % (conf.DB_USER,
    conf.DB_PASS, conf.DB_HOST, conf.DB_NAME)}
    configure_db(options)
