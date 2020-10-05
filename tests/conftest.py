import json
from typing import Any, Dict, List

import pytest


@pytest.fixture
def field_data_with_cell_group() -> List[Any]:
    return [json.load(open("tests/fixtures/field_data_cg.json"), parse_int=str)]


@pytest.fixture
def field_data_with_personal_attribute() -> List[Any]:
    return [json.load(open("tests/fixtures/field_data_personal.json"), parse_int=str)]


@pytest.fixture
def person_data() -> Any:
    return json.load(open("tests/fixtures/person.json"), parse_int=str)


@pytest.fixture
def field_definitions() -> Dict[str, str]:
    # Correct as a 17 Sep 2020
    return {
        "Connect Group": "401410",
        "Salvation Date": "88097",
        "Recommitment Date": "97849",
        "Water Baptism Date": "87410",
        "Holy Spirit Baptism Date": "87411",
        "Encounter Date": "88699",
        "Faith Essentials Begun": "299202",
        "Discipleship Essentials Begun": "283022",
        "Faith Essentials Complete": "283032",
    }
