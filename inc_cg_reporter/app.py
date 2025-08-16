import logging
import os
import pathlib
from datetime import date
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# import boto3
import daiquiri
import pypco

from inc_cg_reporter.connect_group import PersonManager, ConnectGroupMembershipManager
from inc_cg_reporter.field_definition import (
    FieldDataProcessor,
    CONNECT_GROUP_FIELD_DEFINITION_NAME,
    PERSONAL_ATTRIBUTE_NAME,
    PERSONAL_ATTRIBUTE_SINGLE_VALUE_FIELD_DEFINITION_NAMES,
    PERSONAL_ATTRIBUTE_MULTI_VALUE_FIELD_DEFINITION_NAMES,
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


def send_summary_email(saved_file: pathlib.Path):
    msg = MIMEMultipart()
    msg["Subject"] = "INC CG report"
    msg["From"] = "edwin@wordspeak.org"
    msg["To"] = "edwin@wordspeak.org"

    current_datestamp = date.today().strftime("%Y-%m-%d")

    # Set message body
    body = MIMEText(
        "Current INC Connect Group Spreadsheet attached.\n"
        "Reply to this email if you have questions.\n"
        "--Edwin",
        "plain",
    )
    msg.attach(body)

    with open(saved_file, "rb") as attachment:
        part = MIMEApplication(attachment.read())
        part.add_header(
            "Content-Disposition",
            "attachment",
            filename=f"inc_cg-{current_datestamp}.xlsx",
        )
    msg.attach(part)

    # Convert message to string and send
    #ses_client = boto3.client("ses", region_name="us-east-1")
    # response = ses_client.send_raw_email(
    #     Source="edwin@wordspeak.org",
    #     Destinations=["edwin@wordspeak.org"],
    #     RawMessage={"Data": msg.as_string()},
    # )
    # print(response)


def run(event, context) -> None:
    logger.info("Starting...")
    pco = get_pco()
    person_manager = PersonManager()
    connect_group_person_manager = ConnectGroupMembershipManager(person_manager)
    # Pull date and membership data from Planning Centre, populating the person
    #  and connect group person manager instances
    field_data_processor = FieldDataProcessor(
        pco,
        CONNECT_GROUP_FIELD_DEFINITION_NAME,
        PERSONAL_ATTRIBUTE_SINGLE_VALUE_FIELD_DEFINITION_NAMES,
        PERSONAL_ATTRIBUTE_MULTI_VALUE_FIELD_DEFINITION_NAMES,
        person_manager,
        connect_group_person_manager,
    )
    logger.info("Populating person and connect group manager instances")
    field_data_processor.process()
    # Pull people's names from Planning Centre
    logger.info("Pulling people's names and matching with IDs")
    connect_group_person_manager.populate_names_for_people(pco)
    # Now that Names have been populated, we can pass the full list of attributes
    #  to be used as columns, so we know how to generate worksheets for connect groups
    cg_worksheet_generator = ConnectGroupWorksheetGenerator(
        [PERSONAL_ATTRIBUTE_NAME]
        + PERSONAL_ATTRIBUTE_SINGLE_VALUE_FIELD_DEFINITION_NAMES
        + PERSONAL_ATTRIBUTE_MULTI_VALUE_FIELD_DEFINITION_NAMES
    )
    cg_workbook_manager = ConnectGroupWorkbookManager(
        connect_group_person_manager, cg_worksheet_generator
    )
    logger.info("Creating worksheet")
    cg_workbook_manager.create()
    saved_file = cg_workbook_manager.save()
    logger.info("Saved file stored as %s", saved_file.resolve())
    logger.info("Stat info: %s", os.stat(saved_file))
    send_summary_email(saved_file)


if __name__ == "__main__":
    run({}, {})
