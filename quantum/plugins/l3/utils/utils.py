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
# @author: Sumit Naiksatam, Cisco Systems, Inc.
# @author: Rohit Agarwalla, Cisco Systems, Inc.


import logging
import subprocess

from quantum.manager import QuantumManager as manager


LOG = logging.getLogger(__name__)


def get_l2_plugin_reference():
    """
    This method returns a reference to the L2 plugin object
    Warning: This method should only be called after QuantumManager
    has completed initialization, else it will lead to infinite recursion
    """
    return manager.get_plugin()


def strcmp_ignore_case(s1, s2):
    """ Method that takes two strings and returns True or False,
        based on if they are equal, regardless of case."""
    return s1.lower() == s2.lower()


def execute_command_string(cmd):
    """Method to execute commands"""
    try:
        cmd_output = subprocess.Popen(cmd, stdout=subprocess.PIPE).\
                       communicate()[0]
    except Exception as exc:
        print " Failed to execute command %s - %s", \
                                    (cmd, exc)


def extend_string_list(org_str, ext_str):
    """Method to extend a string list"""
    ext_str = ext_str.split(" ")
    org_str.extend(ext_str)
    return org_str
