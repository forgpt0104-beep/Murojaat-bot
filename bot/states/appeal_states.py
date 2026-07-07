"""FSM states for the new-appeal creation flow."""

from aiogram.fsm.state import State, StatesGroup


class AppealStates(StatesGroup):
    """States used while a user is composing a new appeal."""

    waiting_content = State()
    waiting_attach_more = State()
