"""Admin panel: export all appeals to CSV / Excel / PDF."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import BufferedInputFile, CallbackQuery

from bot.database.uow import UnitOfWork
from bot.filters import IsAdminFilter
from bot.keyboards.callback_data import AdminMenuCallback, ExportFormatCallback
from bot.keyboards.inline.admin import export_format_keyboard
from bot.locales import i18n
from bot.services.export_service import ExportService

router = Router(name="admin_export")
router.callback_query.filter(IsAdminFilter())


@router.callback_query(AdminMenuCallback.filter(F.action == "export"))
async def export_entry(call: CallbackQuery, lang: str) -> None:
    await call.message.answer(i18n.get(lang, "export_prompt"), reply_markup=export_format_keyboard(lang))
    await call.answer()


@router.callback_query(ExportFormatCallback.filter())
async def export_run(
    call: CallbackQuery, callback_data: ExportFormatCallback, uow: UnitOfWork, lang: str
) -> None:
    export_service = ExportService(uow)

    if callback_data.fmt == "csv":
        content, filename = await export_service.export_csv()
    elif callback_data.fmt == "excel":
        content, filename = await export_service.export_excel()
    else:
        content, filename = await export_service.export_pdf()

    await call.message.answer_document(BufferedInputFile(content, filename=filename))
    await call.message.answer(i18n.get(lang, "export_done"))
    await call.answer()
