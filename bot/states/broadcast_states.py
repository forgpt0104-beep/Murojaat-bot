"""FSM states for the admin broadcast flow."""

from aiogram.fsm.state import State, StatesGroup


class BroadcastStates(StatesGroup):
    """States used while an admin is composing a broadcast message."""

    waiting_content = State()
    waiting_confirmation = State()
