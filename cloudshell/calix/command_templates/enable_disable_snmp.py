#!/usr/bin/python

from cloudshell.cli.command_template.command_template import CommandTemplate

SHOW_SNMP_CONFIGURATION = CommandTemplate(
    "do show running-config | include snmp-server"
)

ENABLE_SNMP = CommandTemplate("snmp-server enable snmp vrf {vrf}")
DISABLE_SNMP = CommandTemplate("no snmp-server enable snmp vrf {vrf}")

CONFIGURE_VIEW = CommandTemplate("snmp-server view {view} .1 included vrf {vrf}")
REMOVE_VIEW = CommandTemplate("no snmp-server view {view} vrf {vrf}")

CONFIGURE_V2C_COMMUNITY = CommandTemplate(
    "snmp-server community {community} view {view} version v2c ro vrf {vrf}"
)
REMOVE_V2C_COMMUNITY = CommandTemplate("no snmp-server community {community} vrf {vrf}")

CONFIGURE_V3_USER = CommandTemplate(
    "snmp v3 user {snmp_user} authentication protocol {auth_protocol} {auth_pass} "
    "priv {priv_protocol} {priv_key} vrf {vrf}"
)
REMOVE_V3_USER = CommandTemplate("no snmp-server user {snmp_user} vrf {vrf}")
