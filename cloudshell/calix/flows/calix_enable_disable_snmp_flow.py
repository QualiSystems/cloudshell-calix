from __future__ import annotations

import logging
from typing import TYPE_CHECKING, ClassVar

from attrs import define

from cloudshell.snmp.snmp_configurator import EnableDisableSnmpFlowInterface

from cloudshell.calix.command_actions.enable_disable_snmp_actions import (
    EnableDisableSnmpV2Actions,
    EnableDisableSnmpV3Actions,
)
from cloudshell.calix.helpers.exceptions import CalixSNMPException

if TYPE_CHECKING:
    from typing import Union

    from cloudshell.cli.service.cli_service import CliService
    from cloudshell.snmp.snmp_parameters import (
        SNMPReadParameters,
        SNMPV3Parameters,
        SNMPWriteParameters,
    )

    from ..cli.calix_cli_configurator import CalixCliConfigurator

    SnmpParams = Union[SNMPReadParameters, SNMPWriteParameters, SNMPV3Parameters]

logger = logging.getLogger(__name__)


@define
class CalixEnableDisableSnmpFlow(EnableDisableSnmpFlowInterface):
    _cli_configurator: CalixCliConfigurator
    vrf: str
    DEFAULT_SNMP_VIEW: ClassVar[str] = "quali"
    DEFAULT_SNMP_GROUP: ClassVar[str] = "network-operator"
    ENCRYPTION: ClassVar[dict[str, str]] = {
        "MD5": "md5",
        "SHA": "sha",
        "DES": "des",
        "AES-128": "aes",
        "AES-192": "aes",
        "AES-256": "aes",
    }

    def enable_snmp(self, snmp_parameters: SnmpParams) -> None:
        with self._cli_configurator.config_mode_service() as cli_service:
            if snmp_parameters.version == snmp_parameters.SnmpVersion.V3:
                self._enable_snmp_v3(cli_service, snmp_parameters, self.vrf)
            else:
                self._enable_snmp_v2(cli_service, snmp_parameters, self.vrf)

    def disable_snmp(self, snmp_parameters: SnmpParams) -> None:
        with self._cli_configurator.config_mode_service() as cli_service:
            if snmp_parameters.version == snmp_parameters.SnmpVersion.V3:
                self._disable_snmp_v3(cli_service, snmp_parameters, self.vrf)
            else:
                self._disable_snmp_v2(cli_service, snmp_parameters, self.vrf)

    def _enable_snmp_v2(
        self,
        cli_service: CliService,
        snmp_parameters: SnmpParams,
        vrf: str = "management",
    ) -> None:
        """Enable SNMPv2."""
        snmp_community = snmp_parameters.snmp_community

        if not snmp_community:
            raise CalixSNMPException("SNMP community can not be empty")

        snmp_v2_actions = EnableDisableSnmpV2Actions(cli_service=cli_service)
        snmp_v2_actions.configure_snmp_view(view_name=self.DEFAULT_SNMP_VIEW, vrf=vrf)
        current_snmp_config = snmp_v2_actions.current_snmp_configuration()

        if snmp_community not in current_snmp_config.get("communities"):
            snmp_v2_actions.configure_snmp_community(
                community=snmp_community, view=self.DEFAULT_SNMP_VIEW, vrf=vrf
            )
        else:
            logger.debug(f"SNMP Community '{snmp_community}' already configured")

    def _enable_snmp_v3(
        self,
        cli_service: CliService,
        snmp_parameters: SnmpParams,
        vrf: str = "management",
    ) -> None:
        """Enable SNMPv3."""
        snmp_v3_actions = EnableDisableSnmpV3Actions(cli_service=cli_service)
        snmp_v3_actions.configure_snmp_view(view_name=self.DEFAULT_SNMP_VIEW, vrf=vrf)
        current_snmp_config = snmp_v3_actions.current_snmp_configuration()
        if snmp_parameters.snmp_user not in current_snmp_config.get("users"):
            snmp_parameters.validate()
            snmp_v3_actions.configure_snmp_v3(
                snmp_user=snmp_parameters.snmp_user,
                auth_protocol=self.ENCRYPTION.get(snmp_parameters.snmp_auth_protocol),
                auth_pass=snmp_parameters.snmp_password,
                priv_protocol=self.ENCRYPTION.get(
                    snmp_parameters.snmp_private_key_protocol
                ),
                priv_key=snmp_parameters.snmp_private_key,
                vrf=vrf,
            )
        else:
            logger.debug(
                f"SNMP v3 configuration for user {snmp_parameters.snmp_user} already exist"  # noqa: E501
            )

    @staticmethod
    def _disable_snmp_v2(
        cli_service: CliService, snmp_parameters: SnmpParams, vrf: str = "management"
    ) -> None:
        """Disable SNMPv2."""
        snmp_community = snmp_parameters.snmp_community

        if not snmp_community:
            raise CalixSNMPException("SNMP community can not be empty")

        snmp_v2_actions = EnableDisableSnmpV2Actions(cli_service=cli_service)

        snmp_v2_actions.remove_snmp_comminity(
            community=snmp_parameters.snmp_community, vrf=vrf
        )

    @staticmethod
    def _disable_snmp_v3(
        cli_service: CliService, snmp_parameters: SnmpParams, vrf: str = "management"
    ) -> None:
        """Disable SNMPv3."""
        snmp_v3_actions = EnableDisableSnmpV3Actions(cli_service)
        snmp_v3_actions.remove_snmp_v3(snmp_user=snmp_parameters.snmp_user, vrf=vrf)
