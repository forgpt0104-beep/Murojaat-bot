"""Exports the full appeals list to CSV, Excel (xlsx) or PDF."""

from __future__ import annotations

import csv
import io
from datetime import datetime

from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from bot.database.uow import UnitOfWork
from bot.utils.formatting import format_datetime, status_label

HEADERS = [
    "Appeal ID",
    "Status",
    "Language",
    "Created At",
    "User Full Name",
    "Username",
    "Telegram ID",
    "Summary",
]


class ExportService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def _rows(self) -> list[list[str]]:
        appeals = await self.uow.appeals.list_all_for_export()
        rows = []
        for appeal in appeals:
            rows.append(
                [
                    appeal.formatted_number,
                    status_label("en", appeal.status),
                    appeal.language.value,
                    format_datetime(appeal.created_at),
                    appeal.user.full_name,
                    f"@{appeal.user.username}" if appeal.user.username else "",
                    str(appeal.user.telegram_id),
                    (appeal.summary_text or "")[:200],
                ]
            )
        return rows

    async def export_csv(self) -> tuple[bytes, str]:
        rows = await self._rows()
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(HEADERS)
        writer.writerows(rows)

        filename = f"appeals_export_{datetime.now():%Y%m%d_%H%M%S}.csv"
        return buffer.getvalue().encode("utf-8-sig"), filename

    async def export_excel(self) -> tuple[bytes, str]:
        rows = await self._rows()
        wb = Workbook()
        ws = wb.active
        ws.title = "Appeals"
        ws.append(HEADERS)
        for row in rows:
            ws.append(row)

        for column_cells in ws.columns:
            max_length = max(len(str(cell.value or "")) for cell in column_cells)
            ws.column_dimensions[column_cells[0].column_letter].width = min(max_length + 2, 50)

        buffer = io.BytesIO()
        wb.save(buffer)

        filename = f"appeals_export_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
        return buffer.getvalue(), filename

    async def export_pdf(self) -> tuple[bytes, str]:
        rows = await self._rows()
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()

        elements = [Paragraph("Support Bot - Appeals Export", styles["Title"]), Spacer(1, 12)]

        table_data = [HEADERS] + rows
        table = Table(table_data, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTSIZE", (0, 0), (-1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
                ]
            )
        )
        elements.append(table)
        doc.build(elements)

        filename = f"appeals_export_{datetime.now():%Y%m%d_%H%M%S}.pdf"
        return buffer.getvalue(), filename
