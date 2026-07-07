"""FSM states for admin panel flows: search, ban/unban, settings."""

from aiogram.fsm.state import State, StatesGroup


class SearchStates(StatesGroup):
    waiting_query = State()


class BanStates(StatesGroup):
    waiting_target = State()
    waiting_reason = State()


class UnbanStates(StatesGroup):
    waiting_target = State()


class SettingsStates(StatesGroup):
    waiting_value = State()
