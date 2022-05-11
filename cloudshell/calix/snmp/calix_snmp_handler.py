#!/usr/bin/python

from cloudshell.snmp.snmp_configurator import (
    EnableDisableSnmpConfigurator,
    EnableDisableSnmpFlowInterface,
)

from cloudshell.calix.flows.calix_disable_snmp_flow import CalixDisableSnmpFlow
from cloudshell.calix.flows.calix_enable_snmp_flow import CalixEnableSnmpFlow


class CalixEnableDisableSnmpFlow(EnableDisableSnmpFlowInterface):
    DEFAULT_SNMP_VIEW = "quali_snmp_view"
    DEFAULT_SNMP_GROUP = "quali_snmp_group"

    def __init__(self, cli_handler, logger, resource_config):
        """Enable snmp flow."""
        self._logger = logger
        self._cli_handler = cli_handler
        self._resource_config = resource_config

    def enable_snmp(self, snmp_parameters):
        CalixEnableSnmpFlow(self._cli_handler, self._logger).enable_flow(
            snmp_parameters, self._resource_config.vrf_management_name
        )

    def disable_snmp(self, snmp_parameters):
        CalixDisableSnmpFlow(self._cli_handler, self._logger).disable_flow(
            snmp_parameters, self._resource_config.vrf_management_name
        )


class CalixSnmpHandler(EnableDisableSnmpConfigurator):
    def __init__(self, resource_config, logger, cli_handler):
        self.cli_handler = cli_handler
        enable_disable_snmp_flow = CalixEnableDisableSnmpFlow(
            self.cli_handler, logger, resource_config
        )
        super().__init__(enable_disable_snmp_flow, resource_config, logger)
