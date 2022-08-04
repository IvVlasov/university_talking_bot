from config import dp, bot
import buttons as btn
from messages import adm
from aiogram.types import Message, ReplyKeyboardRemove
from services import db
from states.models import Moderation, AdmAddition, BlockUser
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageCantBeEdited, \
    MessageToDeleteNotFound


async def start_moderate(message: Message, first_message: Message):
    """
    Старт модерации неотвеченных вопросов
     """
    quest = await db.moderate_last_no_answer(message.chat.id)
    if not quest:
        await message.answer(adm['no_moder_questions'])
        await dp.get_current().current_state().finish()
        return

    answer_text = f'Вопрос - {quest.text}\n' \
                  f'Введите ответ или удалите'
    await message.answer(answer_text, reply_markup=btn.delete_quest)

    state = await Moderation.start_msg.set()
    await state.update_data(start_msg=first_message.message_id,
                            quest=quest.text,
                            vector=quest.vector,
                            questioner=quest.questioner_id)


@dp.callback_query_handler(lambda c: c.data.startswith('delete'),
                           state=Moderation.start_msg)
async def delete_quest(call, state: FSMContext):
    """ Удаляем вопрос, оставляя его неотвеченным """
    data = await state.get_data()
    await _delete_moderate_msgs(data['start_msg'], call.message)

    answer_msg = await call.message.answer('Вопрос удалён')
    await db.delete_no_answer(call.message.chat.id)
    await start_moderate(call.message, answer_msg)


@dp.message_handler(content_types=['text'],
                    state=Moderation.start_msg)
async def answer(message, state: FSMContext):
    """
    Введён текстовый ответ на вопрос. Cпрашиваем о внесении в основную таблицу ответов
    """
    await state.update_data(answer=message.text)
    await _answer_to_questioner(state)

    await message.answer(adm['answer_delivered'], reply_markup=btn.ask_insert_qa)
    await db.delete_no_answer(message.chat.id)
    await Moderation.next()


@dp.callback_query_handler(lambda c: c.data.startswith('insert_'),
                           state=Moderation.quest)
async def insert_quest(call, state: FSMContext):
    """
    Заносим вопрос в основную таблицу ответов, либо переходим к следующему
    """
    data = await state.get_data()
    await _delete_moderate_msgs(data['start_msg'], call.message)

    match call.data.split('_')[1]:
        case 'yes':
            await db.insert_question_faq(data['quest'],
                                         data['answer'],
                                         data['vector'])
            msg_text = adm['answer_inserted']
        case _:
            msg_text = adm['answer_not_inserted']

    answer_msg = await call.message.answer(msg_text)
    await start_moderate(call.message, answer_msg)


async def _delete_moderate_msgs(start_msg: int, msg_now: Message) -> None:
    """ Удаляем сообщения в диалоге с администратором """
    for msg_id in range(start_msg, msg_now.message_id + 1):
        try:
            await bot.delete_message(chat_id=msg_now.chat.id,
                                     message_id=msg_id)
        except MessageCantBeEdited:
            pass # Пропускаем сообщения если они не найдены
        except MessageToDeleteNotFound:
            pass


async def _answer_to_questioner(state: FSMContext) -> None:
    """ Отправляем ответ пользователю """
    data = await state.get_data()
    msg_text = f'Спрашивали - отвечаем.\n\n' \
               f'{data["quest"]}\n' \
               f'{data["answer"]}'
    await bot.send_message(chat_id=data['questioner'], text=msg_text)


async def _validate_ident(message):
    if not message.text.isdigit():
        await message.reply('id должен быть числовым значением')
        return False

    ident = int(message.text)
    if await db.find_user(ident) is None:
        await message.answer('Пользователь с таким id не найден')
        return False
    return ident


# add admin
async def admin_adding(message):
    await message.answer('Введите chat id пользователя, '
                         'для выдачи прав администратора.',
                         reply_markup=ReplyKeyboardRemove())
    await AdmAddition.ident.set()


@dp.message_handler(content_types=['text'],
                    state=AdmAddition.ident)
async def add_admin(message: Message, state: FSMContext):
    chat_id = await _validate_ident(message)
    if not chat_id:
        return
    await db.update_status(chat_id, 'admin')
    await message.answer(f'Пользователь {message.text} получил админ права')
    await bot.send_message(chat_id=chat_id,
                           text='Вы получили права администратора, введите /adm '
                                'или /admin для открытия админ-панели')
    await state.finish()


# block user
async def blocking_user(message):
    await message.answer('Введите chat id пользователя '
                         'для блокировки.',
                         reply_markup=ReplyKeyboardRemove())
    await BlockUser.ident.set()


@dp.message_handler(content_types=['text'],
                    state=BlockUser.ident)
async def block_user(message: Message, state: FSMContext):
    chat_id = await _validate_ident(message)
    if not chat_id:
        return
    await db.update_status(chat_id, 'blocked')
    await message.answer(f'Пользователь {message.text} забанен')
    await bot.send_message(chat_id=chat_id,
                           text='По решению администратора вы получили '
                                'бан в этом чате.')
    await state.finish()
