from aiogram.fsm.state import StatesGroup, State


class Feedback(StatesGroup):
    waiting_for_text = State()


class EmojiCaptcha(StatesGroup):
    waiting_for_choice = State()


class AdminStates(StatesGroup):
    waiting_for_file = State()
