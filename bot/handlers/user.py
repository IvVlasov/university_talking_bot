from config import dp, bot
from aiogram import types
from messages import msg, adm
import buttons as btn
from services.vectors import Vector
from services import db
from states.models import Report
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Filter


class IsBlocked(Filter):
    async def check(self, message: types.Message) -> bool:
        """ Фильтр заблокированных """
        return await db.find_status(message.chat.id) == 'blocked'



@dp.message_handler(commands=['start'], state='*')
async def start(message: types.Message):
    await db.insert_user(message.chat.id, 'member')
    await message.answer(msg['hello'])


@dp.message_handler(IsBlocked(), state='*')
async def blocked(message: types.Message):
    await message.answer('Вы заблокированы в этом чате')


@dp.message_handler(content_types=['text'], state='*')
async def echo(message: types.message):
    vector = await Vector.create(message)
    answer = await vector.create_answer()

    if answer.table == 'faq' or answer.cosine > 0.85:
        await message.answer(f'{await _format_text(answer.text)}')
        return

    # Нет ответа, старт машины состояний
    await message.answer(msg['no_answer'], reply_markup=btn.send_report)
    state = await Report.last_msg.set()
    await state.update_data(last_msg=message,
                            vector=await vector.create_vector())


async def _format_text(stroke):
    """ Форматируем текст для ответа """
    if 'http' in stroke:
        return stroke
    ls_str = [el.strip().capitalize() for el in stroke.split('.')]
    return '. '.join(ls_str)


@dp.callback_query_handler(lambda c: c.data == 'send_report',
                           state=Report.last_msg)
async def change_quest(call, state: FSMContext):
    """ Нажатие на кнопку "Отправить администратору" """
    data = await state.get_data()
    text = data['last_msg'].text
    user_id = data['last_msg']['from']['id']
    vector = data['vector']

    await db.insert_no_answer(text, vector, user_id)
    await _send_msg_to_admin()

    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=msg['thank_u'],
                                reply_markup=btn.plug)


async def _send_msg_to_admin():
    """ Рассылка администраторам о новом, неотвеченном вопросе"""
    for el in await db.find_admins():
        await bot.send_message(chat_id=el[1], text=adm['new_question'])
