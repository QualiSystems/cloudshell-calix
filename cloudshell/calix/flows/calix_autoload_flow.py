#!/usr/bin/python

import os
import re

from cloudshell.shell.flows.autoload.basic_flow import AbstractAutoloadFlow
from cloudshell.snmp.autoload.services.port_table import PortsTable
from cloudshell.snmp.autoload.snmp.entities.snmp_if_entity import SnmpIfEntity

from cloudshell.calix.autoload.calix_generic_snmp_autoload import (
    CalixGenericSNMPAutoload,
)


class CalixSnmpAutoloadFlow(AbstractAutoloadFlow):
    MIBS_FOLDER = os.path.join(os.path.dirname(__file__), os.pardir, "mibs")

    def __init__(self, logger, snmp_handler):
        super().__init__(logger)
        self._snmp_handler = snmp_handler

    def _autoload_flow(self, supported_os, resource_model):
        SnmpIfEntity.PORT_IDS_PATTERN = re.compile(r"\d+(/\d+)*(\D+\d+)*$")
        PortsTable.PORT_VALID_TYPE_LIST += ["pon"]
        with self._snmp_handler.get_service() as snmp_service:
            snmp_service.add_mib_folder_path(
                os.path.join(os.path.dirname(__file__), "..", "mibs")
            )
            snmp_autoload = CalixGenericSNMPAutoload(
                snmp_service,
                self._logger,
                resource_model=resource_model,
            )

            return snmp_autoload.discover(
                supported_os,
            )
