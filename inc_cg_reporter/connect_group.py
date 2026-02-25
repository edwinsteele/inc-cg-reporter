import logging
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Dict

import daiquiri
import pypco

from inc_cg_reporter.field_definition import PERSONAL_ATTRIBUTE_NAME

daiquiri.setup(level=logging.INFO)
logger = daiquiri.getLogger(__name__)


@dataclass
class Person:
    id: int
    personal_attributes: Dict[str, str] = field(default_factory=dict)


@dataclass
class ConnectGroup:
    name: str
    members: List[Person] = field(default_factory=list)


class PersonManager:

    ADD_EXTEND_SEPARATOR = ","

    def __init__(self):
        self._people: Dict[int, Person] = {}

    def get(self, person_id: int):
        person = self._people.get(person_id)
        if not person:
            person = Person(person_id)
            self._people[person_id] = person

        return person

    def add_attribute(self, field_name: str, field_value: str, person_id: int):
        # XXX - this class manages people, but also dictates how fields are stored
        #  on the person object, which means that the ConnectGroupWorksheetGenerator
        #  needs more detail about the People object than is appropriate.
        # Needs a refactor to extract field mapping methods, principally so that
        #  the CGWG doesn't need to know about the internals of people objects.
        logger.debug(
            "Adding attribute %s with value %s to person with id %s",
            field_name,
            field_value,
            person_id,
        )
        person = self.get(person_id)
        person.personal_attributes[field_name] = field_value

    def add_or_extend_attribute(
        self, field_name: str, field_value: str, person_id: int
    ):
        # Add attribute, preserving existing values if present
        person = self.get(person_id)
        if current_field_value := person.personal_attributes.get(field_name):
            logger.debug(
                "Extending attribute %s (existing value %s) with value %s to person with id %s",
                field_name,
                current_field_value,
                field_value,
                person_id,
            )
            person.personal_attributes[field_name] = (
                current_field_value + self.ADD_EXTEND_SEPARATOR + field_value
            )
        else:
            self.add_attribute(field_name, field_value, person_id)


class ConnectGroupMembershipManager:
    def __init__(self, pm: PersonManager):
        self.connect_groups: Dict[str, ConnectGroup] = {}
        self._person_manager = pm

    def add(self, _: str, connect_group_name: str, person_id: int):
        logger.debug(
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
        if len(person["data"]) > 0:
            return str(person["data"][0]["attributes"]["name"])
        return f"Name Missing (id: {person_id})"

    def populate_names_for_people(self, pco: pypco.PCO):
        unique_person_ids = list({
            person.id
            for cg in self.connect_groups.values()
            for person in cg.members
        })
        logger.info(
            "Fetching names for %d unique people across %d connect groups",
            len(unique_person_ids),
            len(self.connect_groups),
        )

        batch_size = 100
        num_batches = -(-len(unique_person_ids) // batch_size)
        total_fetched = 0

        for batch_num, i in enumerate(
            range(0, len(unique_person_ids), batch_size), start=1
        ):
            batch = unique_person_ids[i : i + batch_size]
            response = pco.get(
                "/people/v2/people",
                per_page=batch_size,
                **{"where[id]": ",".join(str(pid) for pid in batch)},
            )
            returned_ids = set()
            for person_data in response["data"]:
                person_id = int(person_data["id"])
                self._person_manager.add_attribute(
                    PERSONAL_ATTRIBUTE_NAME,
                    str(person_data["attributes"]["name"]),
                    person_id,
                )
                returned_ids.add(person_id)

            for pid in batch:
                if pid not in returned_ids:
                    logger.warning("Name not found in PCO for person id %s", pid)
                    self._person_manager.add_attribute(
                        PERSONAL_ATTRIBUTE_NAME, f"Name Missing (id: {pid})", pid
                    )

            total_fetched += len(returned_ids)
            logger.info(
                "  Batch %d/%d: %d names fetched", batch_num, num_batches, len(returned_ids)
            )

        logger.info(
            "Finished fetching names: %d total in %d batched requests"
            " (previously %d sequential requests)",
            total_fetched,
            num_batches,
            len(unique_person_ids),
        )

    @property
    def connect_groups_count(self):
        return len(self.connect_groups)

    @property
    def connect_groups_member_count(self):
        return sum([len(cg.members) for cg in self.connect_groups.values()])

    @property
    def volunteer_count(self):
        vc = Counter()
        for cg in self.connect_groups.values():
            for member in cg.members:
                team_str = member.personal_attributes.get("Team", "")
                if team_str:
                    vc.update(team_str.split(","))
        return vc
