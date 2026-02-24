from typing import List, Any, Dict

from pretend import stub

from inc_cg_reporter.connect_group import ConnectGroupMembershipManager
from inc_cg_reporter.field_definition import FieldDataProcessor


def test_cg_extraction_from_field_data(
    pco_field_data_with_cell_group,
    field_dispatcher,
    person_manager,
    connect_group_person_manager,
):
    # noinspection PyTypeChecker
    fdp = FieldDataProcessor(
        pco_field_data_with_cell_group,
        "dummy",
        ["dummy"],
        [],
        person_manager,
        connect_group_person_manager,
    )
    fdp.process_field_data(field_dispatcher)
    assert "Sample CG" in connect_group_person_manager.connect_groups
    assert connect_group_person_manager.connect_groups["Sample CG"].name == "Sample CG"
    assert len(connect_group_person_manager.connect_groups["Sample CG"].members) == 1


def test_person_attribute_extraction_from_field_data(
    pco_field_data_with_personal_attribute: List[Any],
    field_dispatcher,
    person_manager,
    connect_group_person_manager,
):
    # noinspection PyTypeChecker
    fdp = FieldDataProcessor(
        pco_field_data_with_personal_attribute,
        "dummy",
        ["dummy"],
        [],
        person_manager,
        connect_group_person_manager,
    )
    fdp.process_field_data(field_dispatcher)
    person = person_manager._people[2373583]
    assert person.id == 2373583
    assert person.personal_attributes["Water Baptism Date"] == "02/11/1997"
    assert connect_group_person_manager.connect_groups == {}


def test_get_person_name_from_id(person_data: Dict[str, str]):
    pco = stub(get=lambda *args, **kwargs: person_data)
    assert (
        ConnectGroupMembershipManager.get_person_name_from_id(pco, 12345) == "Some Guy"
    )
