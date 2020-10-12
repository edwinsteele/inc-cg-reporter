import logging
from dataclasses import dataclass, field
from typing import List, Dict

import daiquiri
import pypco

daiquiri.setup(level=logging.INFO)
logger = daiquiri.getLogger(__name__)


@dataclass
class Person:
    id: int
    name: str = ""
    personal_attributes: Dict[str, str] = field(default_factory=dict)


@dataclass
class ConnectGroup:
    name: str
    members: List[Person] = field(default_factory=list)


class PersonManager:
    def __init__(self):
        self._people: Dict[int, Person] = {}

    def get(self, person_id: int):
        person = self._people.get(person_id)
        if not person:
            person = Person(person_id)
            self._people[person_id] = person

        return person

    def add_attribute(self, field_name: str, field_value: str, person_id: int):
        logger.info(
            "Adding attribute %s with value %s to person with id %s",
            field_name,
            field_value,
            person_id,
        )
        person = self.get(person_id)
        person.personal_attributes[field_name] = field_value


class ConnectGroupPersonManager:
    def __init__(self, pm: PersonManager):
        self.connect_groups: Dict[str, ConnectGroup] = {}
        self._person_manager = pm

    def add(self, _: str, connect_group_name: str, person_id: int):
        logger.info(
            "Adding person %s to Connect Group %s", person_id, connect_group_name
        )
        cg = self.connect_groups.get(connect_group_name)
        if not cg:
            cg = ConnectGroup(connect_group_name)
            self.connect_groups[connect_group_name] = cg

        person = self._person_manager.get(person_id)
        cg.members.append(person)

    @staticmethod
    def get_person_name_from_id(pco: pypco.PCO, person_id: int) -> str:
        params = {"where[id]": person_id}
        person = pco.get("/people/v2/people", **params)
        return str(person["data"][0]["attributes"]["name"])

    def populate_names_for_people(self, pco: pypco.PCO):
        for connect_group in self.connect_groups.values():
            for person in connect_group.members:
                person.name = ConnectGroupPersonManager.get_person_name_from_id(
                    pco, person.id
                )
