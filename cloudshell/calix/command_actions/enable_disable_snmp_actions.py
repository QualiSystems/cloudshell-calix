import re

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)

from cloudshell.calix.command_templates import enable_disable_snmp
from cloudshell.calix.helpers.exceptions import CalixSNMPException


class EnableDisableSnmpActions:
    def __init__(self, cli_service, logger):
        """Enable Disable Snmp actions."""
        self._cli_service = cli_service
        self._logger = logger

    def current_snmp_configuration(self):
        """Show SNMP configuration."""
        output = CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.SHOW_SNMP_CONFIGURATION
        ).execute_command()

        users = list(set(re.findall(r"snmp-server user\s+(?P<user>\w+)", output)))
        communities = list(
            set(re.findall(r"snmp-server community\s+(?P<community>\w+)", output))
        )

        return {"users": users, "communities": communities}

    def enable_snmp_service(self, vrf):
        """Enable SNMP agent and configure SNMP version."""
        CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.ENABLE_SNMP
        ).execute_command(vrf=vrf)

    def disable_snmp_service(self, vrf):
        """Disable SNMP service on the device."""
        CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.DISABLE_SNMP
        ).execute_command(vrf=vrf)

    def configure_snmp_view(self, view_name, vrf):
        """Configure SNMP view."""
        output = CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.CONFIGURE_VIEW
        ).execute_command(view=view_name, vrf=vrf)
        if output.strip().startswith("%"):
            msg = "Configuration SNMP view failed."
            self._logger.error(f"{msg} {output}")
            raise CalixSNMPException(msg)

    def remove_snmp_view(self, view_name, vrf):
        """Remove configured SNMP view."""
        output = CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.REMOVE_VIEW
        ).execute_command(view=view_name, vrf=vrf)
        if output.strip().startswith("%"):
            msg = "Removing SNMP view failed."
            self._logger.error(f"{msg} {output}")
            raise CalixSNMPException(msg)

    def configure_snmp_community(self, community, view, vrf):
        """Configure SNMP v2c community."""
        output = CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.CONFIGURE_V2C_COMMUNITY
        ).execute_command(community=community, view=view, vrf=vrf)
        if output.strip().startswith("%"):
            msg = "Configuration SNMP v2c community failed."
            self._logger.error(f"{msg} {output}")
            raise CalixSNMPException(msg)

    def remove_snmp_comminity(self, community, vrf):
        """Remove SNMP v2c community."""
        output = CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.REMOVE_V2C_COMMUNITY
        ).execute_command(community=community, vrf=vrf)
        if output.strip().startswith("%"):
            msg = "Removing SNMP v2c community failed."
            self._logger.error(f"{msg} {output}")
            raise CalixSNMPException(msg)

    def configure_snmp_v3(
        self,
        snmp_user,
        auth_protocol,
        auth_pass,
        priv_protocol,
        priv_key,
        vrf,
    ):
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
        if output.strip().startswith("%"):
            msg = "Configuration SNMP v3 failed."
            self._logger.error(f"{msg} {output}")
            raise CalixSNMPException(msg)

    def remove_snmp_v3(self, snmp_user, vrf):
        """Remove SNMP v3 user."""
        output = CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.REMOVE_V3_USER
        ).execute_command(snmp_user=snmp_user, vrf=vrf)
        if output.strip().startswith("%"):
            msg = "Removing SNMP v3 configuration failed."
            self._logger.error(f"{msg} {output}")
            raise CalixSNMPException(msg)
