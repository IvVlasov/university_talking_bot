from aiogram.dispatcher.filters.state import State, StatesGroup
from config import dp


class StateElement(State):
    async def set(self):
        """ Переопределяем метод set для возврата текущего состояния """
        state = dp.get_current().current_state()
        await state.finish()
        await state.set_state(self.state)
        return dp.get_current().current_state()


class Report(StatesGroup):
    last_msg = StateElement()
    vector = StateElement()
    quest = StateElement()
    answer = StateElement()


class Moderation(StatesGroup):
    start_msg = StateElement()
    quest = StateElement()
    vector = StateElement()
    questioner = StateElement()


class AdmAddition(StatesGroup):
    ident = StateElement()


class BlockUser(StatesGroup):
    ident = StateElement()
