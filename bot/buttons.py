from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton,\
    InlineKeyboardMarkup, KeyboardButton
from messages import btn_text as btn
from config import flask_url

# Заглушка
plug = InlineKeyboardMarkup()

# Кнопки пользователей
send_report = InlineKeyboardMarkup(row_width=2, resize=True)
send_report_num = InlineKeyboardButton(text='Отправить администратору',
                                       callback_data='send_report')
send_report.add(send_report_num)

# Кнопки администратора
adm_btn = ReplyKeyboardMarkup(resize_keyboard=True)
adm_n1 = KeyboardButton(btn['edit_faq'])
adm_n2 = KeyboardButton(btn['no_answers'])
adm_n3 = KeyboardButton(btn['add_admin'])
adm_n4 = KeyboardButton(btn['block_user'])
adm_btn.add(adm_n1).add(adm_n2).add(adm_n3).add(adm_n4)

delete_quest = InlineKeyboardMarkup(row_width=2, resize=True)
del_q_n1 = InlineKeyboardButton(text='Удалить', callback_data='delete')
delete_quest.add(del_q_n1)

ask_insert_qa = InlineKeyboardMarkup(row_width=1, resize=True)
insert_q_y = InlineKeyboardButton(text='Да', callback_data='insert_yes')
insert_q_n = InlineKeyboardButton(text='Нет', callback_data='insert_no')
ask_insert_qa.add(insert_q_y, insert_q_n)


async def flask_link(chat_id: int):
    menu = InlineKeyboardMarkup(row_width=2, resize=True)
    url = f'{flask_url}/questions?chat_id={chat_id}'
    num1 = InlineKeyboardButton(text='Перейти на сайт', url=url)
    menu.add(num1)
    return menu
