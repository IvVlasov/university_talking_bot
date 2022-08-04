import cfg
import asyncpg
from typing import NamedTuple


class Question(NamedTuple):
    ident: int
    quest: str
    answer: str


async def _create_connection():
    connection = await asyncpg.connect(user=cfg.DB_USER,
                                       database=cfg.DB_NAME,
                                       host=cfg.DB_HOST,
                                       port=cfg.DB_PORT,
                                       password=cfg.DB_PASS)
    return connection


# users
async def find_user_status(chat_id: int) -> None | str:
    conn = await _create_connection()
    res = await conn.fetchrow("SELECT * FROM users WHERE chat_id=$1",
                              chat_id)
    await conn.close()
    if res:
        return res['status']
    return None


# questions
async def _format_result(values: list):
    return [Question(el['id'], el['quest'], el['answer']) for el in values]


async def select_all_faq() -> list:
    conn = await _create_connection()
    res = await conn.fetch("SELECT id, quest, answer FROM qa_faq")
    await conn.close()
    return await _format_result(res)


async def delete_faq_from_id(ident: str) -> None:
    conn = await _create_connection()
    await conn.fetch("DELETE FROM qa_faq WHERE id=$1", int(ident))
    await conn.close()


async def insert_faq(quest: str, answer: str, vector: bytes) -> None:
    conn = await _create_connection()
    await conn.fetch("INSERT INTO qa_faq (quest, answer, vector)"
                     "VALUES ($1, $2, $3)", quest, answer, vector)
    await conn.close()


async def update_faq_from_id(ident: int, quest: str, answer: str,
                             vector: bytes) -> None:
    conn = await _create_connection()
    sql = "UPDATE qa_faq SET quest = $1, answer = $2, vector = $3 WHERE id = $4"
    await conn.fetch(sql, quest, answer, vector, int(ident))
    await conn.close()
