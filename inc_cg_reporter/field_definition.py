from __future__ import annotations
import logging
from typing import Dict, List, Callable

import daiquiri
import pypco

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from inc_cg_reporter.connect_group import (
        ConnectGroupMembershipManager,
        PersonManager,
    )

daiquiri.setup(level=logging.INFO)
logger = daiquiri.getLogger(__name__)


CONNECT_GROUP_FIELD_DEFINITION_NAME = "Connect Group"
PERSONAL_ATTRIBUTE_NAME = "Name"
PERSONAL_ATTRIBUTE_FIELD_DEFINITION_NAMES = [
    "Decision Date",
    "Water Baptism Date",
    "Holy Spirit Baptism Date",
    "Encounter Date",
    "FE Finish",
    "DE 1 Finish",
    "DE 2 Finish",
]


class PlanningCentreFieldDefinitionMapper:
    """Maps planning centre field definition ids to readable field names"""

    def __init__(self, pco: pypco.PCO, field_names: List[str]):
        self.__pco = pco
        self._field_names = field_names
        self.field_defs_id_by_name: Dict[str, int] = {}
        self.field_defs_name_by_id: Dict[int, str] = {}

    def get_field_definition_ids(self) -> Dict[str, int]:
        matching = set(self._field_names)
        field_defs: Dict[str, int] = {}

        params = {"per_page": 100}
        for datum in self.__pco.iterate("/people/v2/field_definitions", **params):
            if (field_name := datum["data"]["attributes"]["name"]) in matching:
                field_defs[field_name] = int(datum["data"]["id"])
                matching.remove(field_name)

        if matching:
            logger.critical("No match found for fields %s", matching)
            raise RuntimeError("Unable to match all field definitions")

        return field_defs

    def build_map(self):
        self.field_defs_id_by_name = self.get_field_definition_ids()
        logger.info(self.field_defs_id_by_name)
        self.field_defs_name_by_id = {
            v: k for k, v in self.field_defs_id_by_name.items()
        }


class PlanningCentreFieldHandler:
    """Routes fields (by field_id) to methods"""

    def __init__(self, pcfdm: PlanningCentreFieldDefinitionMapper):
        self._field_handler_map: Dict[int, Callable[[str, str, int], None]] = {}
        self._field_definition_mapper = pcfdm

    def register_method(
        self, field_name: str, handler: Callable[[str, str, int], None]
    ):
        field_id = self._field_definition_mapper.field_defs_id_by_name[field_name]
        self._field_handler_map[field_id] = handler

    def dispatch_field(self, field_id: int, field_value: str, person_id: int):
        if (
            field_name := self._field_definition_mapper.field_defs_name_by_id.get(
                field_id
            )
        ) :
            self._field_handler_map[field_id](field_name, field_value, person_id)


class FieldDataProcessor:
    def __init__(
        self,
        pco: pypco.PCO,
        connect_group_field_name: str,
        personal_attribute_field_names: List[str],
        pm: PersonManager,
        cgm: ConnectGroupMembershipManager,
    ):
        self.__pco = pco
        self.__connect_group_field_name = connect_group_field_name
        self.__personal_attribute_field_names = personal_attribute_field_names
        self.__pm = pm
        self.__cgm = cgm

    def process_field_data(self, field_dispatcher):
        params = {"per_page": 100}
        for datum in self.__pco.iterate("/people/v2/field_data", **params):
            field_id = datum["data"]["relationships"]["field_definition"]["data"]["id"]
            person_id = datum["data"]["relationships"]["customizable"]["data"]["id"]
            field_value = datum["data"]["attributes"]["value"]
            field_dispatcher.dispatch_field(int(field_id), field_value, int(person_id))

    def process(self):
        field_definition_mapper = PlanningCentreFieldDefinitionMapper(
            self.__pco,
            [self.__connect_group_field_name] + self.__personal_attribute_field_names,
        )
        logger.info("Building map")
        field_definition_mapper.build_map()
        field_handler = PlanningCentreFieldHandler(field_definition_mapper)
        field_handler.register_method(self.__connect_group_field_name, self.__cgm.add)
        for paf_name in self.__personal_attribute_field_names:
            field_handler.register_method(paf_name, self.__pm.add_attribute)
        logger.info("Processing field data")
        self.process_field_data(field_handler)
