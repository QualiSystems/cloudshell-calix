from __future__ import annotations

import re
from typing import TYPE_CHECKING

from cloudshell.shell.flows.autoload.basic_flow import AbstractAutoloadFlow
from cloudshell.snmp.autoload.services.port_table import PortsTable
from cloudshell.snmp.autoload.snmp.entities.snmp_if_entity import SnmpIfEntity

from cloudshell.calix.autoload.calix_generic_snmp_autoload import (
    CalixGenericSNMPAutoload,
)

if TYPE_CHECKING:
    from cloudshell.shell.core.driver_context import AutoLoadDetails
    from cloudshell.shell.standards.networking.autoload_model import (
        NetworkingResourceModel,
    )
    from cloudshell.snmp.snmp_configurator import EnableDisableSnmpConfigurator


class CalixSnmpAutoloadFlow(AbstractAutoloadFlow):
    def __init__(self, snmp_configurator: EnableDisableSnmpConfigurator):
        super().__init__()
        self._snmp_configurator = snmp_configurator

    def _autoload_flow(
        self, supported_os: list[str], resource_model: NetworkingResourceModel
    ) -> AutoLoadDetails:
        """Autoload Flow."""
        SnmpIfEntity.PORT_IDS_PATTERN = re.compile(r"\d+(/\d+)*(\D+\d+)*$")
        PortsTable.PORT_VALID_TYPE_LIST += ["pon"]
        with self._snmp_configurator.get_service() as snmp_service:
            snmp_autoload = CalixGenericSNMPAutoload(
                snmp_service,
                resource_model=resource_model,
            )

            return snmp_autoload.discover(supported_os)
