from flask import Flask, request, render_template
import logging
from services import db
from services.fast_text import get_vector_json_dump, create_vector

application = Flask(__name__)

logger = logging.getLogger("App.Flask")
logger.info('Application started')


async def bad_valid():
    logger.info(msg=f"User - {request.environ['REMOTE_ADDR']}"
                    f"tried connect to API")
    return {'result': "Access denied"}


@application.route("/questions", methods=["GET"])
async def questions():
    chat_id = int(request.args['chat_id'])
    user = await db.find_user_status(chat_id)
    if user == 'admin':
        data = sorted(await db.select_all_faq(), reverse=True)
        return render_template('index.html', data=data)
    else:
        return bad_valid()


@application.route("/search", methods=["GET"])
async def vector():
    chat_id = int(request.args['chat_id'])
    message = request.args.get('string')
    if await db.find_user_status(chat_id) is not None:
        return {'result': await get_vector_json_dump(message)}
    else:
        return bad_valid()


@application.route("/change/", methods=["POST"])
async def change_values():
    parsed = request.json
    try:
        _vector = await create_vector(parsed['quest'])
        await db.update_faq_from_id(parsed['ident'], parsed['quest'],
                                    parsed['answer'], _vector)
    except Exception as e:
        logger.error(e)
        return {'result': 'Ошибка записи в базу данных'}
    return {}


@application.route("/delete/", methods=["POST"])
async def delete_value():
    parsed = request.json
    try:
        await db.delete_faq_from_id(parsed['ident'])
    except Exception as e:
        logger.error(e)
        return {'result': 'Ошибка удаления записи'}
    return {}


@application.route("/insert/", methods=["POST"])
async def insert_value():
    quest = request.json[0]['value']
    answer = request.json[1]['value']
    _vector = await create_vector(quest)
    try:
        await db.insert_faq(quest, answer, _vector)
    except Exception as e:
        logger.error(e)
        return {'result': 'Ошибка занесения новой записи'}
    return {}


if __name__ == "__main__":
    application.run(host='0.0.0.0')
