from gensim.models.fasttext import FastText
import json
import logging
import pickle

logger = logging.getLogger("App.Word2Vec")
logger.info('Opening a file start')
model = FastText.load("services/model/ft_model.model")
logger.info('Opening a file finish')


async def get_vector_json_dump(stroke: str):
    """Находим в пространстве вектор строки stroke
    и сериализуем её для отправки в json """
    string1 = model.wv.get_mean_vector(stroke.split())
    lists = string1.tolist()
    json_str = json.dumps(lists)
    return json_str


async def create_vector(stroke: str):
    string1 = model.wv.get_mean_vector(stroke.split())
    return pickle.dumps(string1)
