import aiohttp
import json
import numpy as np
import pickle
import random
from typing import NamedTuple

import aiogram.types
from sklearn.neighbors import KDTree

from services.db import select_all_vectors


class Answer(NamedTuple):
    text: str
    cosine: float
    table: str


class Vector:
    quest: str
    chat_id: int
    quest_vector: np.ndarray

    @classmethod
    async def create(cls, message: aiogram.types.Message):
        self = Vector()
        self.quest = message.text.lower()
        self.chat_id = message.chat.id
        self.quest_vector = await self.find_vector()
        return self

    async def find_vector(self) -> np.ndarray:
        """ Находит вектор вопроса в пространстве модели """
        session = aiohttp.ClientSession()
        async with session.get(
                f'http://127.0.0.1:5000/search?string={self.quest}&'
                f'chat_id={self.chat_id}') \
                as response:
            json_format = await response.json()
            b_new = json.loads(json_format['result'])
            await session.close()
            return np.array(b_new)

    async def create_vector(self) -> bytes:
        """ Создает вектор для занесения в базу """
        array = await self.find_vector()
        return pickle.dumps(array)

    async def cosine(self, founded_vector: np.ndarray) -> float:
        """ Косинусная мера между двумя векторами """
        return np.dot(founded_vector, self.quest_vector) /\
               (np.linalg.norm(founded_vector) * np.linalg.norm(self.quest_vector))

    async def search_close_vector(self, data: list, count=5) -> tuple:
        """
        Находим ближайший вектор к заданному с
        помощью алгоритма KD дерева
         """
        vectors = np.array([pickle.loads(el[1]) for el in data])
        kdtree = KDTree(vectors, leaf_size=30)
        dest, idn = kdtree.query([self.quest_vector], k=count)
        if 0 not in dest[0]:
            index = idn[0][0]
        else:
            s_elems = [1 if el < 0.2 else 0 for el in dest[0]]
            index = idn[0][
                random.randint(0, sum(s_elems) - 1)] if s_elems != [] else 0
        return index, vectors[index]

    async def create_answer(self) -> tuple:
        """
        Находим ближайшие вектора из 2ух таблиц,
        сравниваем их косинусные меры и выводим ответ с наибольшей мерой
        """
        Vectors = await select_all_vectors()

        all_index, all_vec = await self.search_close_vector(Vectors.speak)
        faq_index, faq_vec = await self.search_close_vector(Vectors.faq, 2)

        cosine_all = await self.cosine(all_vec)
        cosine_faq = await self.cosine(faq_vec)

        if cosine_all > cosine_faq:
            result = Answer(Vectors.speak[all_index][2], cosine_all, 'speak')
        else:
            result = Answer(Vectors.faq[faq_index][2], cosine_faq, 'faq')
        return result
