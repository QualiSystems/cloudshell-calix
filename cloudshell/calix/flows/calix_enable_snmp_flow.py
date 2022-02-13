#!/usr/bin/python

from cloudshell.calix.command_actions.enable_disable_snmp_actions import (  # noqa: E501
    EnableDisableSnmpActions,
)
from cloudshell.calix.helpers.exceptions import CalixSNMPException


class CalixEnableSnmpFlow:
    DEFAULT_SNMP_VIEW = "quali"
    DEFAULT_SNMP_GROUP = "network-operator"
    ENCRYPTION = {
        "MD5": "md5",
        "SHA": "sha",
        "DES": "des",
        "AES-128": "aes",
        "AES-192": "aes",
        "AES-256": "aes",
    }

    def __init__(self, cli_handler, logger):
        """Enable snmp flow."""
        self._logger = logger
        self._cli_handler = cli_handler

    def enable_flow(self, snmp_parameters, vrf="management"):
        if "3" not in snmp_parameters.version and not snmp_parameters.snmp_community:
            message = "SNMP community cannot be empty"
            self._logger.error(message)
            raise CalixSNMPException(message)

        with self._cli_handler.get_cli_service(
            self._cli_handler.config_mode
        ) as config_session:
            snmp_actions = EnableDisableSnmpActions(config_session, self._logger)
            snmp_actions.configure_snmp_view(view_name=self.DEFAULT_SNMP_VIEW, vrf=vrf)
            current_snmp_config = snmp_actions.current_snmp_configuration()
            if "3" in snmp_parameters.version:
                if snmp_parameters.snmp_user not in current_snmp_config.get("users"):
                    snmp_parameters.validate()
                    snmp_actions.configure_snmp_v3(
                        snmp_user=snmp_parameters.snmp_user,
                        auth_protocol=self.ENCRYPTION.get(
                            snmp_parameters.snmp_auth_protocol.upper()
                        ),
                        auth_pass=snmp_parameters.snmp_password,
                        priv_protocol=self.ENCRYPTION.get(
                            snmp_parameters.snmp_private_key_protocol.upper()
                        ),
                        priv_key=snmp_parameters.snmp_private_key,
                        vrf=vrf,
                    )
                else:
                    self._logger.debug(
                        "SNMP v3 configuration for user {} already exist".format(
                            snmp_parameters.snmp_user
                        )
                    )

            else:
                snmp_community = snmp_parameters.snmp_community
                if snmp_community not in current_snmp_config.get("communities"):
                    snmp_actions.configure_snmp_community(
                        community=snmp_community, view=self.DEFAULT_SNMP_VIEW, vrf=vrf
                    )
                else:
                    self._logger.debug(
                        f"SNMP Community '{snmp_community}' already configured"
                    )
