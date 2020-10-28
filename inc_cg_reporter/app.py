import logging
import os

import daiquiri
import pypco

from inc_cg_reporter.connect_group import PersonManager, ConnectGroupPersonManager
from inc_cg_reporter.field_definition import (
    FieldDataProcessor,
    CONNECT_GROUP_FIELD_DEFINITION_NAME,
    PERSONAL_ATTRIBUTE_NAME,
    PERSONAL_ATTRIBUTE_FIELD_DEFINITIONS,
)
from inc_cg_reporter.writer import (
    ConnectGroupWorksheetGenerator,
    ConnectGroupWorkbookManager,
)

daiquiri.setup(level=logging.INFO)
logger = daiquiri.getLogger(__name__)


def get_pco() -> pypco.PCO:
    app_id = os.environ["PC_APPLICATION_ID"]
    app_secret = os.environ["PC_SECRET"]
    return pypco.PCO(app_id, app_secret)


def run() -> None:
    pco = get_pco()
    person_manager = PersonManager()
    connect_group_person_manager = ConnectGroupPersonManager(person_manager)
    # Pull date and membership data from Planning Centre, populating the person
    #  and connect group person manager instances
    fdp = FieldDataProcessor(
        pco,
        CONNECT_GROUP_FIELD_DEFINITION_NAME,
        PERSONAL_ATTRIBUTE_FIELD_DEFINITIONS,
        person_manager,
        connect_group_person_manager,
    )
    fdp.process()
    # Pull people's names from Planning Centre
    connect_group_person_manager.populate_names_for_people(pco)
    # Now that Names have been populated, we can pass the full list of attributes
    #  to be used as columns
    cg_worksheet_generator = ConnectGroupWorksheetGenerator(
        [PERSONAL_ATTRIBUTE_NAME] + PERSONAL_ATTRIBUTE_FIELD_DEFINITIONS
    )
    cg_workbook_manager = ConnectGroupWorkbookManager(
        connect_group_person_manager, cg_worksheet_generator
    )
    cg_workbook_manager.create()
    cg_workbook_manager.save("inc_cg.xlsx")


if __name__ == "__main__":
    run()
