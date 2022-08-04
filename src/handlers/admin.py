from config import dp, spec_simbol
from aiogram import types
from messages import adm, btn_text
import buttons as btn
from aiogram.dispatcher.filters import Filter
from states.moderation import start_moderate, admin_adding, blocking_user
from services import db


class IsAdmin(Filter):
    async def check(self, message: types.Message) -> bool:
        """ Фильтр администратора """
        return await db.find_status(message.chat.id) == 'admin'


class NoAdmins(Filter):
    async def check(self, message: types.Message) -> bool:
        """ В базе нет администраторов """
        return await db.find_admins() == []


@dp.message_handler(NoAdmins(), commands=['adm', 'admin'], state='*')
async def no_admins(message: types.Message):
    await db.update_status(message.chat.id, 'admin')
    await admin_panel(message)


@dp.message_handler(IsAdmin(), commands=['adm', 'admin'], state='*')
async def admin_panel(message: types.Message):
    """ Панель администратора """
    await message.answer(adm['panel'], reply_markup=btn.adm_btn)


@dp.message_handler(lambda msg: msg.text.startswith(spec_simbol),
                    IsAdmin(),
                    content_types=['text'],
                    state='*')
async def admin_text_message(message: types.message):
    if message.text == btn_text['edit_faq']:
        # Редактирование вопросов FAQ
        await message.answer(adm['edit_questions'],
                             reply_markup=await btn.flask_link(message.chat.id))
    elif message.text == btn_text['no_answers']:
        # Неотвеченные вопросы
        start_msg = await message.answer(adm['start_moderate'],
                                         reply_markup=types.ReplyKeyboardRemove())
        await start_moderate(message, start_msg)
    elif message.text == btn_text['add_admin']:
        # Добавить администратора
        await admin_adding(message)
    elif message.text == btn_text['block_user']:
        # Заблокировать пользователя
        await blocking_user(message)
