from typing import List, Dict

from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from inc_cg_reporter.connect_group import (
    ConnectGroup,
    ConnectGroupPersonManager,
    Person,
)


class ConnectGroupWorksheetGenerator:
    def __init__(self, field_list: List[str]):
        self._field_list = field_list
        # name is the first column, and column indexes start from 1 and enumerate
        #  starts uses zero-based counting
        self._column_locations = {
            col_name: col_number + 2
            for col_number, col_name in (enumerate(self._field_list))
        }

    def person_as_row_values(self, person: Person) -> Dict[int, str]:
        row = {1: person.name}
        for column_name, value in person.personal_attributes.items():
            row[self._column_locations[column_name]] = value

        return row

    def populate(self, ws: Worksheet, cg: ConnectGroup):
        ws.title = cg.name
        self.create_column_headers(ws)
        for person in cg.members:
            ws.append(self.person_as_row_values(person))

    def create_column_headers(self, ws: Worksheet):
        ws.cell(row=1, column=1, value="Name")
        for col_name, col_index in self._column_locations.items():
            ws.cell(row=1, column=col_index, value=col_name)


class ConnectGroupWorkbookManager:
    def __init__(
        self,
        cgpm: ConnectGroupPersonManager,
        cgwsg: ConnectGroupWorksheetGenerator,
    ):
        self._cgpm = cgpm
        self._cgwsg = cgwsg

    def create(self) -> Workbook:
        workbook = Workbook()
        for connect_group in self._cgpm.connect_groups.values():
            ws = workbook.create_sheet()
            self._cgwsg.populate(ws, connect_group)

        # Remove the blank sheet that's created initially
        workbook.remove(workbook.worksheets[0])
        return workbook

    def save(self, filename: str):
        wb = self.create()
        wb.save(filename)
