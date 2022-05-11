#!/usr/bin/python
from cloudshell.calix.command_actions.enable_disable_snmp_actions import (  # noqa: E501
    EnableDisableSnmpActions,
)
from cloudshell.calix.helpers.exceptions import CalixSNMPException


class CalixDisableSnmpFlow:
    def __init__(self, cli_handler, logger):
        """Disable SNMP flow."""
        self._cli_handler = cli_handler
        self._logger = logger

    def disable_flow(self, snmp_parameters, vrf="management"):
        if "3" not in snmp_parameters.version and not snmp_parameters.snmp_community:
            message = "SNMP community cannot be empty"
            self._logger.error(message)
            raise CalixSNMPException(message)

        with self._cli_handler.get_cli_service(
            self._cli_handler.config_mode
        ) as config_session:
            snmp_actions = EnableDisableSnmpActions(config_session, self._logger)
            if "3" in snmp_parameters.version:
                snmp_actions.remove_snmp_v3(
                    snmp_user=snmp_parameters.snmp_user, vrf=vrf
                )
            else:
                snmp_actions.remove_snmp_comminity(
                    community=snmp_parameters.snmp_community, vrf=vrf
                )
