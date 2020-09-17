from typing import List, Any, Dict

from pretend import stub

from inc_cg_reporter.app import process_field_data


def test_cg_extraction_from_field_data(
    field_data_with_cell_group: List[Any], field_definitions: Dict[str, str]
):
    pco = stub(iterate=lambda *args, **kwargs: field_data_with_cell_group)
    # noinspection PyTypeChecker
    connect_group_membership, personal_attributes = process_field_data(
        pco, field_definitions
    )
    assert personal_attributes == {}
    assert connect_group_membership == {"Mitch Varlow's CG": ["2373583"]}


def test_person_attribute_extraction_from_field_data(
    field_data_with_personal_attribute: List[Any], field_definitions: Dict[str, str]
):
    pco = stub(iterate=lambda *args, **kwargs: field_data_with_personal_attribute)
    # noinspection PyTypeChecker
    connect_group_membership, personal_attributes = process_field_data(
        pco, field_definitions
    )
    assert personal_attributes == {"2373583": {"87410": "02/11/1997"}}
    assert connect_group_membership == {}
