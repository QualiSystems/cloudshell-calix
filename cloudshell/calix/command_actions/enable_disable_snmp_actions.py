from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING

from attrs import define

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)
from cloudshell.snmp.snmp_parameters import SNMPV3Parameters  # noqa F401

from cloudshell.calix.command_templates import enable_disable_snmp
from cloudshell.calix.helpers.exceptions import CalixSNMPException

if TYPE_CHECKING:
    from cloudshell.cli.service.cli_service import CliService

logger = logging.getLogger(__name__)


@define
class BaseSnmpActions:
    _cli_service: CliService

    def current_snmp_configuration(self) -> dict[str : list[str]]:
        """Show SNMP configuration."""
        output = CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.SHOW_SNMP_CONFIGURATION
        ).execute_command()

        users = list(set(re.findall(r"snmp-server user\s+(?P<user>\w+)", output)))
        communities = list(
            set(re.findall(r"snmp-server community\s+(?P<community>\w+)", output))
        )

        return {"users": users, "communities": communities}

    def enable_snmp_service(self, vrf: str) -> None:
        """Enable SNMP agent and configure SNMP version."""
        CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.ENABLE_SNMP
        ).execute_command(vrf=vrf)

    def disable_snmp_service(self, vrf: str) -> None:
        """Disable SNMP service on the device."""
        CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.DISABLE_SNMP
        ).execute_command(vrf=vrf)

    def configure_snmp_view(self, view_name: str, vrf: str):
        """Configure SNMP view."""
        output = CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.CONFIGURE_VIEW
        ).execute_command(view=view_name, vrf=vrf)
        self._raise_on_error(
            command_output=output, error_char="%", msg="Configuration SNMP view failed."
        )

    def remove_snmp_view(self, view_name: str, vrf: str) -> None:
        """Remove configured SNMP view."""
        output = CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.REMOVE_VIEW
        ).execute_command(view=view_name, vrf=vrf)
        self._raise_on_error(
            command_output=output, error_char="%", msg="Removing SNMP view failed."
        )

    @staticmethod
    def _raise_on_error(command_output: str, error_char: str, msg: str) -> None:
        """Check is command executed successfully."""
        if command_output.strip().startswith(error_char):
            logger.error(f"{msg} {command_output}")
            raise CalixSNMPException(msg)


class EnableDisableSnmpV2Actions(BaseSnmpActions):
    def configure_snmp_community(self, community: str, view: str, vrf: str) -> None:
        """Configure SNMP v2c community."""
        output = CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.CONFIGURE_V2C_COMMUNITY
        ).execute_command(community=community, view=view, vrf=vrf)
        self._raise_on_error(
            command_output=output,
            error_char="%",
            msg="Configuration SNMP v2c community failed.",
        )

    def remove_snmp_comminity(self, community: str, vrf: str) -> None:
        """Remove SNMP v2c community."""
        output = CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.REMOVE_V2C_COMMUNITY
        ).execute_command(community=community, vrf=vrf)
        self._raise_on_error(
            command_output=output,
            error_char="%",
            msg="Removing SNMP v2c community failed.",
        )


class EnableDisableSnmpV3Actions(BaseSnmpActions):
    def configure_snmp_v3(
        self,
        snmp_user: str,
        auth_protocol: str,
        auth_pass: str,
        priv_protocol: str,
        priv_key: str,
        vrf: str,
    ) -> None:
        """Configure SNMP v3."""
        output = CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.CONFIGURE_V3_USER
        ).execute_command(
            snmp_user=snmp_user,
            auth_protocol=auth_protocol,
            auth_pass=auth_pass,
            priv_protocol=priv_protocol,
            priv_key=priv_key,
            vrf=vrf,
        )
        self._raise_on_error(
            command_output=output, error_char="%", msg="Configuration SNMP v3 failed."
        )

    def remove_snmp_v3(self, snmp_user: str, vrf: str) -> None:
        """Remove SNMP v3 user."""
        output = CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.REMOVE_V3_USER
        ).execute_command(snmp_user=snmp_user, vrf=vrf)
        self._raise_on_error(
            command_output=output,
            error_char="%",
            msg="Removing SNMP v3 configuration failed.",
        )
