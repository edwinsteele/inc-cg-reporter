import logging
import os

import daiquiri
import pypco

from inc_cg_reporter.connect_group import PersonManager, ConnectGroupMembershipManager
from inc_cg_reporter.field_definition import (
    FieldDataProcessor,
    CONNECT_GROUP_FIELD_DEFINITION_NAME,
    PERSONAL_ATTRIBUTE_NAME,
    PERSONAL_ATTRIBUTE_FIELD_DEFINITION_NAMES,
)
from inc_cg_reporter.excel_writer import (
    ConnectGroupWorksheetGenerator,
    ConnectGroupWorkbookManager,
)

daiquiri.setup(level=logging.INFO)
logger = daiquiri.getLogger(__name__)


def get_pco() -> pypco.PCO:
    """Returns reuseable Planning Centre Online instance"""
    app_id = os.environ["PC_APPLICATION_ID"]
    app_secret = os.environ["PC_SECRET"]
    return pypco.PCO(app_id, app_secret)


def run(event, context) -> None:
    pco = get_pco()
    person_manager = PersonManager()
    connect_group_person_manager = ConnectGroupMembershipManager(person_manager)
    # Pull date and membership data from Planning Centre, populating the person
    #  and connect group person manager instances
    field_data_processor = FieldDataProcessor(
        pco,
        CONNECT_GROUP_FIELD_DEFINITION_NAME,
        PERSONAL_ATTRIBUTE_FIELD_DEFINITION_NAMES,
        person_manager,
        connect_group_person_manager,
    )
    field_data_processor.process()
    # Pull people's names from Planning Centre
    connect_group_person_manager.populate_names_for_people(pco)
    # Now that Names have been populated, we can pass the full list of attributes
    #  to be used as columns, so we know how to generate worksheets for connect groups
    cg_worksheet_generator = ConnectGroupWorksheetGenerator(
        [PERSONAL_ATTRIBUTE_NAME] + PERSONAL_ATTRIBUTE_FIELD_DEFINITION_NAMES
    )
    cg_workbook_manager = ConnectGroupWorkbookManager(
        connect_group_person_manager, cg_worksheet_generator
    )
    cg_workbook_manager.create()
    saved_file = cg_workbook_manager.save()
    logger.info("Saved file stored as %s", saved_file.resolve())
    logger.info("Stat info: %s", os.stat(saved_file))


if __name__ == "__main__":
    run({}, {})
