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
# @author: Sumit Naiksatam, Cisco Systems, Inc.


"""Implements iptables rules using linux utilities."""


import subprocess

from quantum.plugins.l3.utils import utils as util


class IptablesRule(object):
    """An iptables rule.
    """

    def __init__(self, chain, rule):
        self.chain = chain
        self.rule = rule

    def __eq__(self, other):
        return ((self.chain == other.chain) and
                (self.rule == other.rule))

    def __ne__(self, other):
        return not self == other


class IptablesTable(object):
    """An iptables table."""

    def __init__(self):
        self.chains = set()
        self.rules = []

    def add_chain(self, name):
        """Add chain to a table"""
        if name in self.chains:
            return
        command_string = ["iptables", "-N", name]
        util.execute_command_string(command_string)
        self.chains.add(name)

    def remove_chain(self, name):
        """Remove chain from a table"""
        chain_rules = filter(lambda r: r.chain == name, self.rules)
        for rule_obj in chain_rules:
            command_string = ["iptables", "-D", name]
            command_string = util.extend_string_list(command_string,
                                                     rule_obj.rule)
            util.execute_command_string(command_string)
        self.rules = filter(lambda r: r.chain != name, self.rules)

        jump_snippet = '-j %s' % (name,)
        command_string = ["iptables", "-D", "FORWARD"]
        command_string = util.extend_string_list(command_string, jump_snippet)
        util.execute_command_string(command_string)
        self.rules = filter(lambda r: jump_snippet not in r.rule, self.rules)

        command_string = ["iptables", "-X", name]
        util.execute_command_string(command_string)
        self.chains.remove(name)

    def add_rule(self, chain, rule, insert=False, pos=None):
        """Add a rule to a chain
        """
        if not insert:
            command_string = ["iptables", "-A", chain]
        else:
            command_string = ["iptables", "-I", chain, pos]
        command_string = util.extend_string_list(command_string, rule)
        if IptablesRule(chain, rule) in self.rules:
            return
        util.execute_command_string(command_string)
        self.rules.append(IptablesRule(chain, rule))

    def remove_rule(self, chain, rule):
        """Remove a rule from a chain.
        """
        command_string = ["iptables", "-D", chain]
        command_string = util.extend_string_list(command_string, rule)
        util.execute_command_string(command_string)
        self.rules.remove(IptablesRule(chain, rule))


class IptablesManager(object):
    """Wrapper for iptables.
    """

    def __init__(self):
        self.ipv4 = {'filter': IptablesTable()}

    def subnet_public_accept(self, subnet):
        """Allow subnet to internet traffic
        """
        self.ipv4['filter'].remove_rule("l3-linux-FORWARD", \
                                     "-s %(subnet)s ! -d %(subnet)s" \
                                     " -j DROP" % {'subnet': subnet})

    def subnet_public_drop(self, subnet):
        """Deny subnet to internet traffic
        """
        self.ipv4['filter'].add_chain("l3-linux-FORWARD")
        self.ipv4['filter'].add_rule("FORWARD", "-j l3-linux-FORWARD", \
                                      True, "1")
        self.ipv4['filter'].add_rule("l3-linux-FORWARD", \
                                     "-s %(subnet)s ! -d %(subnet)s" \
                                     " -j DROP" % {'subnet': subnet})

    def clear_all(self, chain_name):
        """Remove chain and all rules in that chain
        """
        self.ipv4['filter'].remove_chain(chain_name)

    def add_iptable_rule(self, source, destination, subnet, target):
        """Add iptables rule based on the route rule
        """
        if util.strcmp_ignore_case(destination, const.DESTINATION_DEFAULT)\
           and util.strcmp_ignore_case(target, const.TARGET_PUBLIC):
            self.subnet_public_drop(subnet)

    def remove_iptable_rule(self, source, destination, subnet, target):
        """Remove iptables rule based on the route rule
        """
        if util.strcmp_ignore_case(destination, const.DESTINATION_DEFAULT)\
           and util.strcmp_ignore_case(target, const.TARGET_PUBLIC):
            self.subnet_public_accept(subnet)


if __name__ == '__main__':
    iptables_manager = IptablesManager()

    option = raw_input("Enter q/c/d/a")
    while (option != "q"):
        if (option == "c"):
            iptables_manager.clear_all("l3-linux-FORWARD")
        elif (option == "d"):
            iptables_manager.subnet_public_drop("10.0.0.0/8")
        elif (option == "a"):
            iptables_manager.subnet_public_accept("10.0.0.0/8")
        else:
            print "Invalid option"
        option = raw_input("Enter q/c/d/a")
