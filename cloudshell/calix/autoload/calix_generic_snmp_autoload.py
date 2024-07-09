from __future__ import annotations

from functools import lru_cache

from cloudshell.snmp.autoload.constants.entity_constants import (
    ENTITY_MODEL,
    ENTITY_OS_VERSION,
    ENTITY_SERIAL,
)
from cloudshell.snmp.autoload.exceptions.snmp_autoload_error import GeneralAutoloadError
from cloudshell.snmp.autoload.generic_snmp_autoload import GenericSNMPAutoload
from cloudshell.snmp.autoload.helper.snmp_autoload_helper import log_autoload_details
from cloudshell.snmp.autoload.snmp.tables.snmp_entity_table import SnmpEntityTable

from cloudshell.calix.autoload.calix_phys_table import CalixPhysicalTable
from cloudshell.calix.autoload.snmp_system_info import CalixSnmpSystemInfo


class CalixGenericSNMPAutoload(GenericSNMPAutoload):
    @property
    @lru_cache()
    def snmp_physical_structure(self) -> SnmpEntityTable:
        return CalixPhysicalTable(
            snmp_handler=self.snmp_handler,
            logger=self.logger,
        )

    @property
    def system_info_service(self):
        if not self._system_info:
            self._system_info = CalixSnmpSystemInfo(self.snmp_handler, self.logger)
        return self._system_info

    def discover(
        self,
        supported_os: list[str] | str,
    ):
        """An entry point for autoload.

        Read device structure and attributes:
        chassis, modules, submodules, ports, port-channels and power supplies.

        :rtype: cloudshell.shell.core.driver_context.AutoLoadDetails
        """
        try:
            if not self.system_info_service.is_valid_device_os(supported_os):
                raise GeneralAutoloadError("Unsupported device OS")

            self.logger.info("*" * 70)
            self.logger.info("Start SNMP discovery process .....")
            self.system_info_service.fill_attributes(self._resource_model)
            self._build_chassis()
            self._build_power_ports()
            self._build_ports_structure()
            self._get_port_channels()
            self.logger.info("SNMP discovery process finished successfully")
            self._update_modules(self._resource_model)
            autoload_details = self._resource_model.build()

            log_autoload_details(self.logger, autoload_details)
            return autoload_details
        finally:
            self._destroy_threads()

    def _update_modules(self, result):
        for child in result.extract_sub_resources():
            if child.cloudshell_model_name in ["GenericModule", "GenericChassis"]:
                self._update_modules(child)
            elif child.cloudshell_model_name == "GenericSubModule":
                child_id = (
                    f"{child.relative_address.parent_node.index}."
                    f"{child.relative_address.index}"
                )
                data = self.snmp_physical_structure.physical_structure_snmp_table.get(
                    child_id, {}
                )
                model = data.get(ENTITY_MODEL.object_name, "")
                child.model_name = model
                child.model = model
                child.serial_number = str(data.get(ENTITY_SERIAL.object_name, ""))
                child.version = str(data.get(ENTITY_OS_VERSION.object_name, ""))
