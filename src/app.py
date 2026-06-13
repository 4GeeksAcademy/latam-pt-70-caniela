"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Torneo, Premios
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", " ://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


@app.route('/torneos', methods=['GET'])
def get_torneos():
    torneos = Torneo.query.all()
    return jsonify([item.serialize() for item in torneos]), 200


@app.route('/torneos/<int:torneo_id>', methods=['GET'])
def get_torneo(torneo_id):

    searched_torneo = Torneo.query.get(torneo_id)

    if searched_torneo is None:
        raise APIException("Torneo no encontrado", status_code=404)

    return jsonify(searched_torneo.serialize()), 200


def getVal(request_body, fields):
    for field in fields:
        value = request_body.get(field)
        if not value:
            raise APIException(
                f"Se debe proveer un valor para {field}", status_code=400)

    return [request_body.get(field) for field in fields]


@app.route('/torneos', methods=['POST'])
def add_torneo():

    body = request.get_json()
    name, sede, finicio, ffinal = getVal(
        body, ['name', 'sede', 'finicio', 'ffinal'])

    new_torneo = Torneo(name=name, sede=sede,
                        fecha_inicio=finicio, fecha_final=ffinal)

    try:
        db.session.add(new_torneo)
        db.session.commit()

    except Exception as e:
        raise APIException("Error al crear el torneo", status_code=500) from e

    return jsonify({
        "msg": "Creando un torneo",
        "torneo": new_torneo.serialize()
    }), 201


@app.route('/premios', methods=['GET'])
def get_premios():
    premios = Premios.query.all()
    return jsonify([item.serialize() for item in premios]), 200


@app.route('/premios/<int:torneo_id>', methods=['POST'])
def add_premio(torneo_id):

    body = request.get_json()
    name, descripcion = getVal(
        body, ['name', 'descripcion'])

    new_premio = Premios(
        nombre=name, descripcion=descripcion, torneo_id=torneo_id)

    try:
        db.session.add(new_premio)
        db.session.commit()

    except Exception as e:
        raise APIException("Error al crear el premio", status_code=500) from e

    return jsonify({
        "msg": "Creando un premio",
        "premio": new_premio.serialize()
    }), 201


@app.route('/premios/<int:premio_id>', methods=['PATCH'])
def edit_premios(premio_id):

    searched_premio = Premios.query.get(premio_id)

    if not searched_premio:
        raise APIException(
            f"No se ha encontrado ese premio_id en la db", status_code=404)

    body = request.get_json()

    name = body.get("name")
    descripcion = body.get("descripcion")

    try:
        if name:
            searched_premio.nombre = name
        if descripcion:
            searched_premio.descripcion = descripcion

        db.session.commit()

    except Exception as e:
        raise APIException(
            f"Something wrong happened", status_code=500
        )

    return jsonify({
        "premio": searched_premio.serialize()
    }), 200


@app.route('/premios/<int:premio_id>', methods=['DELETE'])
def delete_premio(premio_id):

    searched_premio = Premios.query.get(premio_id)

    if not searched_premio:
        raise APIException(
            f"No se ha encontrado ese premio_id en la db", status_code=404)

    try:
        db.session.delete(searched_premio)
        db.session.commit()

    except Exception as e:
        raise APIException(
            f"Something wrong happened", status_code=500
        )

    return jsonify({
        "msg": "Premio eliminado"
    }), 200


@app.route('/torneos/<int:torneo_id>', methods=['DELETE'])
def delete_torneo(torneo_id):

    searched_torneo = Torneo.query.get(torneo_id)

    if not searched_torneo:
        raise APIException(
            f"No se ha encontrado ese torneo_id en la db", status_code=404)

    try:
        db.session.delete(searched_torneo)
        db.session.commit()

    except Exception as e:
        raise APIException(
            f"Something wrong happened", status_code=500
        )

    return jsonify({
        "msg": "Torneo eliminado"
    }), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
