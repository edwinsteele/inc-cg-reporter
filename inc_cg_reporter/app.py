import functools
import logging
import os
from collections import defaultdict
from typing import Dict, List, Set, Tuple

import daiquiri
import pypco


daiquiri.setup(level=logging.INFO)
logger = daiquiri.getLogger(__name__)


CONNECT_GROUP_FIELD_DEFINITION_NAME = "Connect Group"
PERSONAL_FIELD_DEFINITIONS = [
    "Salvation Date",
    "Recommitment Date",
    "Water Baptism Date",
    "Holy Spirit Baptism Date",
    "Encounter Date",
    "Faith Essentials Begun",
    "Discipleship Essentials Begun",
    "Faith Essentials Complete",
]


def get_pco() -> pypco.PCO:
    app_id = os.environ["PC_APPLICATION_ID"]
    app_secret = os.environ["PC_SECRET"]
    return pypco.PCO(app_id, app_secret)


def get_field_definition_ids(pco: pypco.PCO, matching: Set[str]) -> Dict[str, str]:
    logger.info("Retrieving field definition ids")
    field_defs: Dict[str, str] = {}
    params = {"per_page": 100}
    for datum in pco.iterate("/people/v2/field_definitions", **params):
        if (field_name := datum["data"]["attributes"]["name"]) in matching:
            field_defs[field_name] = datum["data"]["id"]
            matching.remove(field_name)

    if matching:
        logger.critical("No match found for fields %s", matching)
        raise RuntimeError("Unable to match all field definitions")

    return field_defs


def process_field_data(
    pco: pypco.PCO, field_definitions: Dict[str, str]
) -> Tuple[Dict[str, List[str]], Dict[str, Dict[str, str]]]:
    # "Edwin Steele": {"87410": "1/1/2000", ... <other fieldid:value mappings>}
    personal_attributes: Dict[str, Dict[str, str]] = defaultdict(dict)
    # "Mitch Varlows CG": ["2373583", ... <other person ids>]
    connect_group_membership: Dict[str, List[str]] = defaultdict(list)
    params = {"per_page": 100}
    for datum in pco.iterate("/people/v2/field_data", **params):
        field_id = datum["data"]["relationships"]["field_definition"]["data"]["id"]
        person_id = datum["data"]["relationships"]["customizable"]["data"]["id"]
        # Handle Connect Group relationship
        if field_id == field_definitions[CONNECT_GROUP_FIELD_DEFINITION_NAME]:
            cg_name = datum["data"]["attributes"]["value"]
            logger.info("Adding person %s to Connect Group %s", person_id, cg_name)
            connect_group_membership[cg_name].append(person_id)
            continue

        # Handle other attributes - this is a bit ugly, because it's unclear that
        #  the remaining ones are personal attributes, and it's brittle if other
        #  types of attributes are added.
        if field_id in field_definitions.values():
            field_value = datum["data"]["attributes"]["value"]
            logger.info("Adding attribute %s to person %s", field_value, person_id)
            personal_attributes[person_id][field_id] = field_value

    return connect_group_membership, personal_attributes


@functools.lru_cache
def get_person_name_from_id(pco: pypco.PCO, person_id: str) -> str:
    params = {"where[id]": person_id}
    person = pco.get("/people/v2/people", **params)
    return str(person["data"][0]["attributes"]["name"])


def run() -> None:
    pco = get_pco()
    # params = {
    #     'where[first_name]': 'Edwin',
    #     'where[last_name]': 'Steele',
    # }
    all_field_definitions = set(
        PERSONAL_FIELD_DEFINITIONS + [CONNECT_GROUP_FIELD_DEFINITION_NAME]
    )
    field_defs_id_by_name = get_field_definition_ids(pco, all_field_definitions)
    logger.info(field_defs_id_by_name)
    connect_group_membership, personal_attributes = process_field_data(
        pco, field_defs_id_by_name
    )

    field_defs_name_by_id = {v: k for k, v in field_defs_id_by_name.items()}
    for connect_group, member_list in connect_group_membership.items():
        logger.info("### Connect Group: %s ###", connect_group)
        for person_id in member_list:
            logger.info("- %s", get_person_name_from_id(pco, person_id))
            for field_id, field_value in personal_attributes[person_id].items():
                logger.info("%s: %s", field_defs_name_by_id[field_id], field_value)


if __name__ == "__main__":
    run()
