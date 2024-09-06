from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import os
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from bson import ObjectId
from database import db
from collectionsTM import *
#from dotenv import load_dotenv

#load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']
CORS(app)
jwt = JWTManager(app)

#Routes Usuario
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = db.Usuarios.find_one({'correoUsuario': data.get('correoUsuario')})
    if user:
        if check_password_hash(user['contrasenaUsuario'], data.get('contrasenaUsuario')):
            identity = {
                'user_id': str(user['_id']),
                'nombreUsuario': user['nombreUsuario'],
                'rolUsuario': user['rolUsuario']
            }
            access_token = create_access_token(identity=identity)
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({'mensaje': 'Contraseña incorrecta'}), 401
    else:
        return jsonify({'mensaje': 'No existe este usuario'}), 404

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    nuevo_usuario = Usuario(
        nombreUsuario=data['nombreUsuario'],
        correoUsuario=data['correoUsuario'],
        contrasenaUsuario=data['contrasenaUsuario'],
        estadoUsuario=data['estadoUsuario'],
        rolUsuario=data['rolUsuario']
    )
    if db.Usuarios.find_one({ "correoUsuario": nuevo_usuario.get_correoUsuario()}):
        return jsonify({'mensaje': 'Este usuario ya existe'}), 400
    else:
        result = db.Usuarios.insert_one(nuevo_usuario.toDBCollection())
        nuevo_usuario._id = result.inserted_id
        identity = {
            'user_id': str(nuevo_usuario._id),
            'nombreUsuario': nuevo_usuario.get_nombreUsuario(),
            'rolUsuario': nuevo_usuario.get_rolUsuario()
        }
        access_token = create_access_token(identity=identity)
        return jsonify(access_token=access_token), 200
    
@app.route('/addpre/<id>', methods=['PUT'])
def addpre(id):
    if not ObjectId.is_valid(id):
        return jsonify({'mensaje': 'ID no válido'}), 400

    object_id = ObjectId(id)

    usuario = db.Usuarios.find_one({'_id': object_id})
    
    if usuario:
        preferencias_nuevas = request.json.get('preferencias', [])
        db.Usuarios.update_one(
            {'_id': object_id},
            {'$set': {'preferencias': preferencias_nuevas}}
        )
        return jsonify({'mensaje': 'Usuario actualizado exitosamente'}), 200
    else:
        return jsonify({'mensaje': 'El usuario no existe'}), 404

@app.route('/get_users', methods=['GET'])
def get_users():
    users = db.Usuarios.find()
    lista_usuarios = []
    for usuario in users:
        lista_usuarios.append({
            '_id': str(usuario['_id']),
            'nombreUsuario': usuario['nombreUsuario'],
            'correoUsuario': usuario['correoUsuario'],
            'contrasenaUsuario': usuario['contrasenaUsuario'],
            'estadoUsuario': usuario['estadoUsuario'],
            'rolUsuario': usuario['rolUsuario'],
        })
    return jsonify(lista_usuarios), 200

@app.route('/search_user', methods=['GET'])
def search_user():

    search_term = request.args.get('q')
    
    if not search_term:
        return jsonify({'mensaje': 'No se proporcionó un término de búsqueda'}), 400

    query_conditions = []

    if ObjectId.is_valid(search_term):
        query_conditions.append({'_id': ObjectId(search_term)})
    query_conditions.append({'nombreUsuario': {'$regex': search_term, '$options': 'i'}})
    query_conditions.append({'correoUsuario': {'$regex': search_term, '$options': 'i'}})
    query_conditions.append({'estadoUsuario': {'$regex': search_term, '$options': 'i'}})
    query_conditions.append({'rolUsuario': {'$regex': search_term, '$options': 'i'}})

    usuarios = db.Usuarios.find({'$or': query_conditions})

    lista_usuarios = []
    for usuario in usuarios:
        lista_usuarios.append({
            '_id': usuario['_id'],
            'nombreUsuario': usuario['nombreUsuario'],
            'correoUsuario': usuario['correoUsuario'],
            'contrasenaUsuario': usuario['contrasenaUsuario'],
            'estadoUsuario': usuario['estadoUsuario'],
            'rolUsuario': usuario['rolUsuario']
        })

    if lista_usuarios:
        return jsonify(lista_usuarios), 200
    else:
        return jsonify({'mensaje': 'No se encontraron usuarios con ese criterio de búsqueda'}), 404
    
@app.route('/update_user/<id>', methods=['PUT'])
def update_user(id):
    if not ObjectId.is_valid(id):
        return jsonify({'mensaje': 'ID no válido'}), 400

    object_id = ObjectId(id)

    usuario = db.Usuarios.find_one({'_id': object_id})
    if usuario:
        data = request.json
        db.Usuarios.update_one(
            {'_id': object_id},
            {'$set': {
                'nombreUsuario': data.get('nombreUsuario', usuario['nombreUsuario']),
                'estadoUsuario': data.get('estadoUsuario', usuario['estadoUsuario']),
                'rolUsuario': data.get('rolUsuario', usuario['rolUsuario'])
            }}
        )
        return jsonify({'mensaje': 'Usuario actualizado exitosamente'}), 200
    else:
        return jsonify({'mensaje': 'El usuario no existe'}), 404

@app.route('/update_pass/<id>', methods=['PUT'])
def update_pass(id):
    if not ObjectId.is_valid(id):
        return jsonify({'mensaje': 'ID no válido'}), 400

    object_id = ObjectId(id)

    usuario = db.Usuarios.find_one({'_id': object_id})
    if usuario:
        data = request.json
        contrasena_antigua = data.get('oldPass')
        if not check_password_hash(usuario['contrasenaUsuario'], contrasena_antigua):
            return jsonify({'mensaje': 'La contraseña antigua no es correcta'}), 400
        
        nueva_contrasena = data.get('contrasenaUsuario')
        if nueva_contrasena:
            nueva_contrasena = generate_password_hash(nueva_contrasena)
        else:
            nueva_contrasena = usuario['contrasenaUsuario']
        
        db.Usuarios.update_one(
            {'_id': object_id},
            {'$set': {
                'contrasenaUsuario': nueva_contrasena,
                'estadoUsuario': data.get('estadoUsuario', usuario['estadoUsuario']),
                'rolUsuario': data.get('rolUsuario', usuario['rolUsuario'])
            }}
        )
        return jsonify({'mensaje': 'Usuario actualizado exitosamente'}), 200
    else:
        return jsonify({'mensaje': 'El usuario no existe'}), 404

@app.route('/delete_user/<id>', methods=['DELETE'])
def delete_user(id):
    if not ObjectId.is_valid(id):
        return jsonify({'mensaje': 'ID no válido'}), 400

    object_id = ObjectId(id)

    usuario = db.Usuarios.find_one({'_id': object_id})

    if usuario:
        db.Usuarios.delete_one({'_id': object_id})
        return jsonify({'mensaje': 'Usuario eliminado exitosamente'}), 200
    else:
        return jsonify({'mensaje': 'No se encontraron usuarios'}), 404


#Routes SitioTuristico
@app.route('/new_item', methods=['POST'])
def registerTuristicPlace():
    data = request.json
    nuevo_sitio = SitiosTuristicos(
            nombreSitiosTuristicos= data['nombreSitiosTuristicos'],
            descripcionSitiosTuristicos= data['descripcionSitiosTuristicos'],
            altitudSitiosTuristicos= data['altitudSitiosTuristicos'],
            latitudSitiosTuristicos= data['latitudSitiosTuristicos'],
            delta='0.01',
            horariosSitiosTuristicos= data['horariosSitiosTuristicos'],
            estadoSitiosTuristicos= data['estadoSitiosTuristicos'],
    )
    db.SitiosTuristicos.insert_one(nuevo_sitio.toDBCollection())
    return jsonify({'mensaje': 'Sitio turistico creado exitosamente'}), 201

@app.route('/get_item', methods=['GET'])
def getTuristicPlaces():
    sitios = db.SitiosTuristicos.find()
    lista_sitios = []
    for sitio in sitios:
        lista_sitios.append({
            '_id': str(sitio['_id']),
            'nombreSitiosTuristicos': sitio['nombreSitiosTuristicos'],
            'descripcionSitiosTuristicos': sitio['descripcionSitiosTuristicos'],
            'altitudSitiosTuristicos': sitio['altitudSitiosTuristicos'],
            'altitudDelta': sitio['altitudDelta'],
            'latitudSitiosTuristicos': sitio['latitudSitiosTuristicos'],
            'latitudDelta': sitio['latitudDelta'],
            'horariosSitiosTuristicos': sitio['horariosSitiosTuristicos'],
            'estadoSitiosTuristicos': sitio['estadoSitiosTuristicos']
        })
    return jsonify(lista_sitios), 200

@app.route('/search_item', methods=['GET'])
def searchItem():

    search_term = request.args.get('q')
    
    if not search_term:
        return jsonify({'mensaje': 'No se proporcionó un término de búsqueda'}), 400

    query_conditions = []

    if ObjectId.is_valid(search_term):
        query_conditions.append({'_id': ObjectId(search_term)})
        query_conditions.append({'nombreSitiosTuristicos': {'$regex': search_term, '$options': 'i'}})

    sitios = db.SitiosTuristicos.find({'$or': query_conditions})

    lista_sitios = []
    for sitio in sitios:
        lista_sitios.append({
            '_id': str(sitio['_id']),
            'nombreSitiosTuristicos': sitio['nombreSitiosTuristicos'],
            'descripcionSitiosTuristicos': sitio['descripcionSitiosTuristicos'],
            'altitudSitiosTuristicos': sitio['altitudSitiosTuristicos'],
            'altitudDelta': sitio['altitudDelta'],
            'latitudSitiosTuristicos': sitio['latitudSitiosTuristicos'],
            'latitudDelta': sitio['latitudDelta'],
            'horariosSitiosTuristicos': sitio['horariosSitiosTuristicos'],
            'estadoSitiosTuristicos': sitio['estadoSitiosTuristicos']
        })

    if lista_sitios:
        return jsonify(lista_sitios), 200
    else:
        return jsonify({'mensaje': 'No se encontraron usuarios con ese criterio de búsqueda'}), 404
    
@app.route('/update_item/<id>', methods=['PUT'])
def update_sitio(id):
    if not ObjectId.is_valid(id):
        return jsonify({'mensaje': 'ID no válido'}), 400

    object_id = ObjectId(id)

    sitio = db.SitiosTuristicos.find_one({'_id': object_id})
    if sitio:
        data = request.json

        db.SitiosTuristicos.update_one(
            {'_id': object_id},
            {'$set': {
                'nombreSitiosTuristicos': data.get('nombreSitiosTuristicos', sitio['nombreSitiosTuristicos']),
                'descripcionSitiosTuristicos': data.get('descripcionSitiosTuristicos', sitio['descripcionSitiosTuristicos']),
                'altitudSitiosTuristicos': data.get('altitudSitiosTuristicos', sitio['altitudSitiosTuristicos']),
                'latitudSitiosTuristicos': data.get('latitudSitiosTuristicos', sitio['latitudSitiosTuristicos']),
                'horariosSitiosTuristicos': data.get('horariosSitiosTuristicos', sitio['horariosSitiosTuristicos']),
                'estadoSitiosTuristicos': data.get('estadoSitiosTuristicos', sitio['estadoSitiosTuristicos'])
            }}
        )
        return jsonify({'mensaje': 'Sitio Turistico actualizado exitosamente'}), 200
    else:
        return jsonify({'mensaje': 'El sitio turistico no existe'}), 404

@app.route('/delete_item/<id>', methods=['DELETE'])
def delete_sitio(id):
    if not ObjectId.is_valid(id):
        return jsonify({'mensaje': 'ID no válido'}), 400

    object_id = ObjectId(id)

    sitio = db.SitiosTuristicos.find_one({'_id': object_id})

    if sitio:
        db.SitiosTuristicos.delete_one({'_id': object_id})
        return jsonify({'mensaje': 'Sitio turistico eliminado exitosamente'}), 200
    else:
        return jsonify({'mensaje': 'No se encontraron sitios'}), 404


#Start app
if __name__ == "__main__":
    app.run()