import json
from typing import Any, List

import pytest
from pretend import stub

from inc_cg_reporter.connect_group import ConnectGroupMembershipManager, PersonManager
from inc_cg_reporter.field_definition import (
    PlanningCentreFieldDefinitionMapper,
    PlanningCentreFieldHandler,
    CONNECT_GROUP_FIELD_DEFINITION_NAME,
    PERSONAL_ATTRIBUTE_SINGLE_VALUE_FIELD_DEFINITION_NAMES,
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
        "FE Start": 299202,
        "FE Finish": 283032,
        "DE Start": 283022,
        "DE Finish": 420172,
    }
    fdm.field_defs_name_by_id = {v: k for k, v in fdm.field_defs_id_by_name.items()}
    return fdm


@pytest.fixture
def person_manager():
    return PersonManager()


@pytest.fixture
def connect_group_person_manager(person_manager):
    return ConnectGroupMembershipManager(person_manager)


@pytest.fixture
def field_dispatcher(
    field_definition_mapper, person_manager, connect_group_person_manager
) -> PlanningCentreFieldHandler:
    field_dispatcher = PlanningCentreFieldHandler(field_definition_mapper)
    field_dispatcher.register_method(
        CONNECT_GROUP_FIELD_DEFINITION_NAME, connect_group_person_manager.add
    )
    for paf_name in PERSONAL_ATTRIBUTE_SINGLE_VALUE_FIELD_DEFINITION_NAMES:
        field_dispatcher.register_method(paf_name, person_manager.add_attribute)
    return field_dispatcher
