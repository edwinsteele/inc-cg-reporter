import json
from typing import Any, List

import pypco
import pytest
from pretend import stub

from inc_cg_reporter.connect_group import ConnectGroupPersonManager, PersonManager
from inc_cg_reporter.field_definition import (
    PlanningCentreFieldDefinitionMapper,
    PlanningCentreFieldDispatcher,
    CONNECT_GROUP_FIELD_DEFINITION_NAME,
    PERSONAL_ATTRIBUTE_FIELD_DEFINITIONS,
)


@pytest.fixture
def field_data_with_cell_group() -> List[Any]:
    return [json.load(open("tests/fixtures/field_data_cg.json"), parse_int=str)]


@pytest.fixture
def pco_field_data_with_cell_group(field_data_with_cell_group):
    return stub(iterate=lambda *args, **kwargs: field_data_with_cell_group)


@pytest.fixture
def field_data_with_personal_attribute() -> List[Any]:
    return [json.load(open("tests/fixtures/field_data_personal.json"), parse_int=str)]


@pytest.fixture
def pco_field_data_with_personal_attribute(field_data_with_personal_attribute):
    return stub(iterate=lambda *args, **kwargs: field_data_with_personal_attribute)


@pytest.fixture
def person_data() -> Any:
    return json.load(open("tests/fixtures/person.json"), parse_int=str)


@pytest.fixture
def field_definition_mapper() -> PlanningCentreFieldDefinitionMapper:
    # Correct as a 17 Sep 2020
    fdm = PlanningCentreFieldDefinitionMapper("dummy", [])
    fdm.field_defs_id_by_name = {
        "Connect Group": 401410,
        "Salvation Date": 88097,
        "Recommitment Date": 97849,
        "Water Baptism Date": 87410,
        "Holy Spirit Baptism Date": 87411,
        "Encounter Date": 88699,
        "Faith Essentials Begun": 299202,
        "Discipleship Essentials Begun": 283022,
        "Faith Essentials Complete": 283032,
    }
    fdm.field_defs_name_by_id = {v: k for k, v in fdm.field_defs_id_by_name.items()}
    return fdm


@pytest.fixture
def person_manager():
    return PersonManager()


@pytest.fixture
def connect_group_person_manager(person_manager):
    return ConnectGroupPersonManager(person_manager)


@pytest.fixture
def field_dispatcher(
    field_definition_mapper, person_manager, connect_group_person_manager
) -> PlanningCentreFieldDispatcher:
    field_dispatcher = PlanningCentreFieldDispatcher(field_definition_mapper)
    field_dispatcher.register(
        CONNECT_GROUP_FIELD_DEFINITION_NAME, connect_group_person_manager.add
    )
    for paf_name in PERSONAL_ATTRIBUTE_FIELD_DEFINITIONS:
        field_dispatcher.register(paf_name, person_manager.add_attribute)
    return field_dispatcher
