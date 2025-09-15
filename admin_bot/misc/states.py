from aiogram.fsm.state import StatesGroup, State


class UploadGrenade(StatesGroup):
    waiting_for_video = State()
    waiting_for_cover = State()
    waiting_for_setup_pic = State()
    waiting_for_finish_pic = State()
    checking_data = State()


class AdminStates(StatesGroup):
    waiting_for_file = State()
