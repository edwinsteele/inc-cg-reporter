import logging
import os

import daiquiri
import pypco

from inc_cg_reporter import field_definition
from inc_cg_reporter.connect_group import PersonManager, ConnectGroupPersonManager
from inc_cg_reporter.field_definition import (
    FieldDataProcessor,
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
    fdp = FieldDataProcessor(
        pco,
        field_definition.CONNECT_GROUP_FIELD_DEFINITION_NAME,
        field_definition.PERSONAL_ATTRIBUTE_FIELD_DEFINITIONS,
        person_manager,
        connect_group_person_manager,
    )
    fdp.process()
    connect_group_person_manager.populate_names_for_people(pco)
    cg_worksheet_generator = ConnectGroupWorksheetGenerator(
        field_definition.PERSONAL_ATTRIBUTE_FIELD_DEFINITIONS
    )
    cg_workbook_manager = ConnectGroupWorkbookManager(
        connect_group_person_manager, cg_worksheet_generator
    )
    cg_workbook_manager.save("inc_cg.xlsx")


if __name__ == "__main__":
    run()
