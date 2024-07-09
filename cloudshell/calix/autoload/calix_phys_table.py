from functools import lru_cache

from cloudshell.snmp.autoload.constants.entity_constants import (
    ENTITY_DESCRIPTION,
    ENTITY_MODEL,
    ENTITY_OS_VERSION,
    ENTITY_PARENT_ID,
    ENTITY_POSITION,
    ENTITY_SERIAL,
)
from cloudshell.snmp.autoload.snmp.tables.snmp_entity_table import SnmpEntityTable
from cloudshell.snmp.core.domain.quali_mib_table import QualiMibTable
from cloudshell.snmp.core.domain.snmp_oid import SnmpMibObject


class AxosResponse:
    def __init__(self, response):
        self.response = response

    def safe_value(self, key, default):
        return self.response.get(key, default)


class CalixPhysicalTable(SnmpEntityTable):
    CARD_TABLE_REQUIRED_COLUMNS = [
        SnmpMibObject("Axos-Card-MIB", "axosCardShelf"),
        SnmpMibObject("Axos-Card-MIB", "axosCardSlot"),
        SnmpMibObject("Axos-Card-MIB", "axosCardCleiCode"),
        SnmpMibObject("Axos-Card-MIB", "axosCardSerialNumber"),
        SnmpMibObject("Axos-Card-MIB", "axosCardSoftwareVersion"),
    ]

    @property
    @lru_cache()
    def physical_structure_snmp_table(self):
        return self._convert_calix_to_entity()

    def _convert_calix_to_entity(self):
        result = QualiMibTable("Entity")
        response = self._snmp_service.get_multiple_columns(
            self.CARD_TABLE_REQUIRED_COLUMNS
        )
        for key, item in response.items():
            shelf_id = item.get("axosCardShelf")
            if shelf_id not in result:
                result[shelf_id] = {
                    ENTITY_DESCRIPTION.object_name: AxosResponse(f"Shelf {shelf_id}"),
                    ENTITY_PARENT_ID.object_name: AxosResponse("0"),
                    ENTITY_POSITION.object_name: shelf_id,
                }
            if key not in result:
                result[key] = {
                    ENTITY_OS_VERSION.object_name: item.get("axosCardSoftwareVersion"),
                    ENTITY_SERIAL.object_name: item.get("axosCardSerialNumber"),
                    ENTITY_PARENT_ID.object_name: shelf_id,
                    ENTITY_MODEL.object_name: item.get("axosCardCleiCode"),
                    ENTITY_POSITION.object_name: item.get("axosCardSlot"),
                }

        return result
