#!/usr/bin/python

import os

from cloudshell.calix.autoload.calix_generic_snmp_autoload import (
    CalixGenericSNMPAutoload,
)
from cloudshell.shell.flows.autoload.basic_flow import AbstractAutoloadFlow


class CalixSnmpAutoloadFlow(AbstractAutoloadFlow):
    MIBS_FOLDER = os.path.join(os.path.dirname(__file__), os.pardir, "mibs")

    def __init__(self, logger, snmp_handler):
        super().__init__(logger)
        self._snmp_handler = snmp_handler

    def _autoload_flow(self, supported_os, resource_model):
        with self._snmp_handler.get_service() as snmp_service:
            snmp_autoload = CalixGenericSNMPAutoload(snmp_service, self._logger)

            return snmp_autoload.discover(
                supported_os, resource_model, validate_module_id_by_port_name=False
            )
