import logging
import os

import daiquiri
import pypco

from inc_cg_reporter import field_definition
from inc_cg_reporter.connect_group import PersonManager, ConnectGroupPersonManager
from inc_cg_reporter.field_definition import (
    FieldDataProcessor,
)

daiquiri.setup(level=logging.INFO)
logger = daiquiri.getLogger(__name__)


def get_pco() -> pypco.PCO:
    app_id = os.environ["PC_APPLICATION_ID"]
    app_secret = os.environ["PC_SECRET"]
    return pypco.PCO(app_id, app_secret)


def run() -> None:
    pco = get_pco()
    # params = {
    #     'where[first_name]': 'Edwin',
    #     'where[last_name]': 'Steele',
    # }
    person_manager = PersonManager()
    connect_group_person_manager = ConnectGroupPersonManager(person_manager)
    fdp = FieldDataProcessor(
        pco,
        field_definition.CONNECT_GROUP_FIELD_DEFINITION_NAME,
        field_definition.PERSONAL_ATTRIBUTE_FIELD_DEFINITIONS,
        person_manager,
        connect_group_person_manager,
    )
    fdp.process()
    connect_group_person_manager.populate_names_for_people(pco)
    print(connect_group_person_manager)
    # Create a data frame for each connect group, with columns as personal field definitions
    # Add each person to the dataframe (which method?
    #  see here: https://stackoverflow.com/questions/15819050/pandas-dataframe-concat-vs-append)
    # Then either df to excel, or create sheets within a OpenPyXL workbook
    #  (https://openpyxl.readthedocs.io/en/stable/pandas.html)
    # (https://realpython.com/openpyxl-excel-spreadsheets-python/)
    # for connect_group, member_list in connect_group_membership.items():
    #     logger.info("### Connect Group: %s ###", connect_group)
    #     for person_id in member_list:
    #         logger.info("- %s", get_person_name_from_id(pco, person_id))
    #         for field_id, field_value in personal_attributes[person_id].items():
    #             logger.info("%s: %s", field_defs_name_by_id[field_id], field_value)


if __name__ == "__main__":
    run()
