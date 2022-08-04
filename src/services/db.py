import asyncpg
import config
from typing import NamedTuple


async def _create_connection():
    connection = await asyncpg.connect(user=config.DB_USER,
                                       database=config.DB_NAME,
                                       host=config.DB_HOST,
                                       port=config.DB_PORT,
                                       password=config.DB_PASS)
    return connection


# qa_faq and qa_speak table
class Vectors(NamedTuple):
    faq: list
    speak: list


async def select_all_vectors() -> Vectors:
    conn = await _create_connection()
    faq_res = await conn.fetch("SELECT id, vector, answer FROM qa_faq")
    speak_res = await conn.fetch("SELECT id, vector, answer FROM qa_speak")
    await conn.close()
    return Vectors(list(faq_res), list(speak_res))


# qa_faq table
async def insert_question_faq(quest: str, answer: str, vector: bytes) -> None:
    conn = await _create_connection()
    await conn.fetch("INSERT INTO qa_faq (quest, answer, vector)"
                     "VALUES ($1, $2, $3)", quest, answer, vector)
    await conn.close()


# no_answer table
async def insert_no_answer(quest: str, vector: bytes, user_ident: int) -> None:
    conn = await _create_connection()
    await conn.fetch("INSERT INTO no_answer (quest, vector, questioner_id )"
                     "VALUES ($1, $2, $3)", quest, vector, user_ident)
    await conn.close()


class Moderation_quest(NamedTuple):
    ident: int
    text: str
    questioner_id: int
    vector: bytes


async def moderate_last_no_answer(new_id: int) -> Moderation_quest | bool:
    conn = await _create_connection()
    await conn.fetch("DELETE FROM no_answer WHERE id=$1", new_id)
    res = await conn.fetchrow(
        "SELECT id, quest, questioner_id, vector  FROM no_answer "
        "WHERE id= (SELECT min(id) FROM no_answer)")
    if res is None:
        return False
    await conn.fetch("UPDATE no_answer SET id = $1 WHERE id = $2", new_id,
                     res['id'])
    await conn.close()
    return Moderation_quest(res['id'],
                            res['quest'],
                            res['questioner_id'],
                            res['vector'])


async def delete_no_answer(admin_id: int) -> None:
    conn = await _create_connection()
    await conn.fetch("DELETE FROM no_answer WHERE id=$1", admin_id)
    await conn.close()


#  users
async def find_user(chat_id: int) -> asyncpg.Record:
    conn = await _create_connection()
    res = await conn.fetchrow("SELECT chat_id FROM users WHERE chat_id=$1",
                              chat_id)
    await conn.close()
    return res


async def insert_user(chat_id: int, status: str):
    conn = await _create_connection()
    if await find_user(chat_id) is None:
        await conn.fetch("INSERT INTO users (chat_id, status) "
                         "VALUES ($1, $2)", chat_id, status)
        await conn.close()


async def find_status(chat_id: int):
    conn = await _create_connection()
    res = await conn.fetchrow("SELECT status FROM users WHERE chat_id=$1",
                              chat_id)
    await conn.close()
    return res['status']


async def find_admins():
    conn = await _create_connection()
    res = await conn.fetch("SELECT * FROM users WHERE status='admin'")
    await conn.close()
    return res


async def update_status(chat_id: int, new_status: str):
    conn = await _create_connection()
    await conn.fetch("UPDATE users SET status = $1 "
                     "WHERE chat_id = $2", new_status, chat_id)
    await conn.close()
