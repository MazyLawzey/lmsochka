from flask import request, jsonify
from flask_cors import CORS



#==============================#
#                              #
#    server.py - main file!    #
#                              #
#==============================#

# иницилизируем сервер, проверим файлы и папки, подключим БД.
def init_server():
    from . import app
    from . import db
    from . import utils

    # проверим папки и файлы, если их нет - создадим их.
    utils.check_files_and_folders()

    # подключаем БД
    db.init_db()

    # разрешаем кросс-доменные запросы (для фронта)
    CORS(app)

