from typing import List, Any, Dict

from pretend import stub

from inc_cg_reporter.connect_group import ConnectGroupMembershipManager, PersonManager
from inc_cg_reporter.field_definition import FieldDataProcessor, PERSONAL_ATTRIBUTE_NAME


def make_people_response(*people):
    """Build a minimal PCO /people/v2/people response for (id, name) pairs."""
    return {"data": [{"id": str(pid), "attributes": {"name": name}} for pid, name in people]}


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


def test_populate_names_happy_path(person_manager, connect_group_person_manager):
    connect_group_person_manager.add("", "Alpha CG", 111)
    connect_group_person_manager.add("", "Alpha CG", 222)

    pco = stub(get=lambda *args, **kwargs: make_people_response((111, "Alice"), (222, "Bob")))
    connect_group_person_manager.populate_names_for_people(pco)

    assert person_manager._people[111].personal_attributes[PERSONAL_ATTRIBUTE_NAME] == "Alice"
    assert person_manager._people[222].personal_attributes[PERSONAL_ATTRIBUTE_NAME] == "Bob"


def test_populate_names_missing_person(person_manager, connect_group_person_manager):
    connect_group_person_manager.add("", "Alpha CG", 111)
    connect_group_person_manager.add("", "Alpha CG", 222)

    # PCO returns only person 111; person 222 is missing from the response
    pco = stub(get=lambda *args, **kwargs: make_people_response((111, "Alice")))
    connect_group_person_manager.populate_names_for_people(pco)

    assert person_manager._people[111].personal_attributes[PERSONAL_ATTRIBUTE_NAME] == "Alice"
    assert person_manager._people[222].personal_attributes[PERSONAL_ATTRIBUTE_NAME] == "Name Missing (id: 222)"


def test_populate_names_deduplicates_across_connect_groups(
    person_manager, connect_group_person_manager
):
    # Person 111 appears in two CGs; should only be included in one batch request
    connect_group_person_manager.add("", "Alpha CG", 111)
    connect_group_person_manager.add("", "Beta CG", 111)

    calls = []

    def tracking_get(*args, **kwargs):
        calls.append(kwargs)
        return make_people_response((111, "Alice"))

    connect_group_person_manager.populate_names_for_people(stub(get=tracking_get))

    assert len(calls) == 1
    assert "111" in calls[0]["where[id]"]
    assert person_manager._people[111].personal_attributes[PERSONAL_ATTRIBUTE_NAME] == "Alice"


# ---------------------------------------------------------------------------
# PersonManager.add_or_extend_attribute
# ---------------------------------------------------------------------------

def test_add_or_extend_attribute_sets_first_value():
    pm = PersonManager()
    pm.add_or_extend_attribute("Team", "Worship", 1)
    assert pm._people[1].personal_attributes["Team"] == "Worship"


def test_add_or_extend_attribute_extends_existing_value():
    pm = PersonManager()
    pm.add_or_extend_attribute("Team", "Worship", 1)
    pm.add_or_extend_attribute("Team", "Kids", 1)
    assert pm._people[1].personal_attributes["Team"] == "Worship,Kids"
