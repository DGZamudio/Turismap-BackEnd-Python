from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import os
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from bson import ObjectId
from database import db
from collectionsTM import *
from math import ceil
import base64
from werkzeug.utils import secure_filename
from gridfs import GridFS
#from dotenv import load_dotenv

#load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']
CORS(app)
jwt = JWTManager(app)
fs = GridFS(db)

#Routes Usuario
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = db.Usuarios.find_one({'correoUsuario': data.get('correoUsuario')})
    if user:
        if check_password_hash(user['contrasenaUsuario'], data.get('contrasenaUsuario')):
            if user['estadoUsuario'] != '1':
                return jsonify({'mensaje':'Usuario inactivo'}), 401
            identity = {
                'user_id': str(user['_id']),
                'nombreUsuario': user['nombreUsuario'],
                'rolUsuario': user['rolUsuario']
            }
            if 'preferencias' in user:
                identity['preferencias'] = user['preferencias']
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
        identity = {
            'user_id': str(object_id),
            'nombreUsuario': usuario.get('nombreUsuario'),
            'rolUsuario': usuario.get('rolUsuario'),
            'preferencias': usuario.get('preferencias')
        }
        access_token = create_access_token(identity=identity)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({'mensaje': 'El usuario no existe'}), 404

@app.route('/get_users/<page>/<limit>', methods=['GET'])
def get_users(page,limit):
    skip = (page - 1) * limit

    users = db.Usuarios.find().skip(skip).limit(limit)
    total_users = db.Usuarios.count_documents({})  
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

    return jsonify({
        'total': total_users,
        'page': page,
        'pages': (total_users + limit - 1) // limit,
        'data': lista_usuarios
    }), 200


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
            '_id': str(usuario['_id']),
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
        identity = {
            'user_id': str(usuario['_id']),
            'nombreUsuario': data.get('nombreUsuario'),
            'rolUsuario': data.get('rolUsuario')
        }
        if 'preferencias' in usuario:
            identity['preferencias'] = usuario['preferencias']
        access_token = create_access_token(identity=identity)
        return jsonify(access_token=access_token), 200
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
    
@app.route('/ban/<id>/<state>', methods=['PUT'])
def ban(id, state):
    if not ObjectId.is_valid(id):
        return jsonify({'mensaje': 'ID no válido'}), 400

    object_id = ObjectId(id)

    usuario = db.Usuarios.find_one({'_id': object_id})

    if usuario:
        if state == '1':
            db.Usuarios.update_one(
            {'_id': object_id},
            {'$set': {'estadoUsuario': '0'}})
            return jsonify({'mensaje':'Usuario desactivado'}), 200
        else:
            db.Usuarios.update_one(
            {'_id': object_id},
            {'$set': {'estadoUsuario': '1'}})
            return jsonify({'mensaje':'Usuario activado'}), 200 
    else:
        return jsonify({'mensaje': 'No se encontro el usuario'}), 404
    
#Routes SitioTuristico
@app.route('/banS/<id>/<state>', methods=['PUT'])
def banS(id,state):
    if not ObjectId.is_valid(id):
        return jsonify({'mensaje': 'ID no válido'}), 400

    object_id = ObjectId(id)

    site = db.SitiosTuristicos.find_one({'_id': object_id})

    if site:
        if state == '1':
            db.SitiosTuristicos.update_one(
            {'_id': object_id},
            {'$set': {'estadoSitiosTuristicos': '0'}})
            return jsonify({'mensaje':'Sitio desactivado'}), 200
        else:
            db.SitiosTuristicos.update_one(
            {'_id': object_id},
            {'$set': {'estadoSitiosTuristicos': '1'}})
            return jsonify({'mensaje':'Sitio activado'}), 200 
    else:
        return jsonify({'mensaje': 'No se encontro el sitio'}), 404  

@app.route('/new_item', methods=['POST'])
def registerTuristicPlace():
    data = request.form
    
    image = request.files.get('image')

    if image and image.filename:
        filename = secure_filename(image.filename)
        file_id = fs.put(image, filename=filename)
    else:
        file_id = ''

    nuevo_sitio = SitiosTuristicos(
            nombreSitiosTuristicos= data['nombreSitiosTuristicos'],
            descripcionSitiosTuristicos= data['descripcionSitiosTuristicos'],
            altitudSitiosTuristicos= data['altitudSitiosTuristicos'],
            latitudSitiosTuristicos= data['latitudSitiosTuristicos'],
            horariosSitiosTuristicos= data['horariosSitiosTuristicos'],
            estadoSitiosTuristicos= data['estadoSitiosTuristicos'],
            tipoSitiosTuristicos= data['tipoSitiosTuristicos'],
            image_id= file_id
    )
    db.SitiosTuristicos.insert_one(nuevo_sitio.toDBCollection())
    return jsonify({'mensaje': 'Sitio turistico creado exitosamente'}), 201

@app.route('/last',methods=['GET'])
def last():
    sitios=db.SitiosTuristicos.find().limit(5)
    result=[]
    for sitio in sitios:
        file_id = sitio.get("image_id")
        image_base64 = None
        if file_id:
            try:
                file_data = fs.get(file_id)
                image_bytes = file_data.read()
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            except Exception as e:
                print(f"Error al obtener la imagen: {e}")

        image = str(image_base64)

        result.append({
            '_id': str(sitio['_id']),
            'nombreSitiosTuristicos': sitio.get('nombreSitiosTuristicos'),
            'estadoSitiosTuristicos': sitio.get('estadoSitiosTuristicos'),
            'image': image
        })
    return jsonify(result), 200

@app.route('/filter/<id>', methods=['GET'])
def filter(id):
    if not ObjectId.is_valid(id):
        return jsonify({'mensaje': 'ID no válido'}), 400

    object_id = ObjectId(id)
    
    user = db.Usuarios.find_one({'_id': object_id})

    if not user:
        return jsonify({'mensaje': 'No se encontró usuario'}), 404
    
    preferencias = user['preferencias']
    query = {'tipoSitiosTuristicos': {'$in': preferencias}, 'estadoSitiosTuristicos': '1'}
    
    page = request.args.get('page', 1, type=int) 
    per_page = request.args.get('per_page', 5, type=int)
    
    skip = (page - 1) * per_page

    sitios_cursor = db.SitiosTuristicos.find(query).skip(skip).limit(per_page)
    total_sitios = db.SitiosTuristicos.count_documents(query)
    total_pages = ceil(total_sitios / per_page)

    result = []

    for sitio in sitios_cursor:

        result.append({
            '_id': str(sitio['_id']),
            'nombreSitiosTuristicos': sitio.get('nombreSitiosTuristicos'),
            'descripcionSitiosTuristicos': sitio.get('descripcionSitiosTuristicos'),
            'altitudSitiosTuristicos': sitio.get('altitudSitiosTuristicos'),
            'latitudSitiosTuristicos': sitio.get('latitudSitiosTuristicos'),
            'horariosSitiosTuristicos': sitio.get('horariosSitiosTuristicos'),
            'tipoSitiosTuristicos': sitio.get('tipoSitiosTuristicos'),
            'estadoSitiosTuristicos': sitio.get('estadoSitiosTuristicos')
        })

    response = {
        "page": page,
        "per_page": per_page,
        "total": total_sitios,
        "total_pages": total_pages,
        "data": result
    }

    return jsonify(response)

@app.route('/filtr', methods=['POST'])
def filtr():

    data = request.json
    preferencias = data['sitio']

    query = {'tipoSitiosTuristicos': {'$in': preferencias}, 'estadoSitiosTuristicos': '1'}
    
    page = request.args.get('page', 1, type=int) 
    per_page = request.args.get('per_page', 5, type=int)
    
    skip = (page - 1) * per_page

    sitios = db.SitiosTuristicos.find(query).skip(skip).limit(per_page)
    total_sitios = db.SitiosTuristicos.count_documents(query)
    total_pages = ceil(total_sitios / per_page)

    result = []

    for sitio in sitios:

        result.append({
            '_id': str(sitio['_id']),
            'nombreSitiosTuristicos': sitio.get('nombreSitiosTuristicos'),
            'descripcionSitiosTuristicos': sitio.get('descripcionSitiosTuristicos'),
            'altitudSitiosTuristicos': sitio.get('altitudSitiosTuristicos'),
            'latitudSitiosTuristicos': sitio.get('latitudSitiosTuristicos'),
            'horariosSitiosTuristicos': sitio.get('horariosSitiosTuristicos'),
            'tipoSitiosTuristicos': sitio.get('tipoSitiosTuristicos'),
            'estadoSitiosTuristicos': sitio.get('estadoSitiosTuristicos')
        })

    response = {
        "page": page,
        "per_page": per_page,
        "total": total_sitios,
        "total_pages": total_pages,
        "data": result
    }

    return jsonify(response)

@app.route('/get_image/<id>', methods=['GET'])
def getImage(id):
    if not ObjectId.is_valid(id):
        return jsonify({'mensaje': 'ID no válido'}), 400

    object_id = ObjectId(id)
    sitio = db.SitiosTuristicos.find_one({'_id': object_id})

    file_id = sitio.get("image_id")
    image_base64 = None
    if file_id:
        try:
            file_data = fs.get(file_id)
            image_bytes = file_data.read()
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        except Exception as e:
            print(f"Error al obtener la imagen: {e}")

    image = str(image_base64)

    return (image), 200

from flask import request

@app.route('/get_item/<page>/<limit>', methods=['GET'])
def getTuristicPlaces(page, limit):
    skip = (page - 1) * limit

    sitios = db.SitiosTuristicos.find().skip(skip).limit(limit)
    total_sitios = db.SitiosTuristicos.count_documents({})  
    lista_sitios = []
    
    for sitio in sitios:
        lista_sitios.append({
            '_id': str(sitio['_id']),
            'nombreSitiosTuristicos': sitio['nombreSitiosTuristicos'],
            'descripcionSitiosTuristicos': sitio['descripcionSitiosTuristicos'],
            'altitudSitiosTuristicos': sitio['altitudSitiosTuristicos'],
            'latitudSitiosTuristicos': sitio['latitudSitiosTuristicos'],
            'horariosSitiosTuristicos': sitio['horariosSitiosTuristicos'],
            'tipoSitiosTuristicos': sitio['tipoSitiosTuristicos'],
            'estadoSitiosTuristicos': sitio['estadoSitiosTuristicos']
        })

    return jsonify({
        'total': total_sitios,
        'page': page,
        'pages': (total_sitios + limit - 1) // limit,  
        'data': lista_sitios
    }), 200


@app.route('/get_sites', methods=['GET'])
def getSites():
    sitios = db.SitiosTuristicos.find({'estadoSitiosTuristicos':'1'})
    lista_sitios = []
    for sitio in sitios:
        lista_sitios.append({
            '_id': str(sitio['_id']),
            'nombreSitiosTuristicos': sitio['nombreSitiosTuristicos'],
            'descripcionSitiosTuristicos': sitio['descripcionSitiosTuristicos'],
            'altitudSitiosTuristicos': sitio['altitudSitiosTuristicos'],
            'latitudSitiosTuristicos': sitio['latitudSitiosTuristicos'],
            'horariosSitiosTuristicos': sitio['horariosSitiosTuristicos'],
            'tipoSitiosTuristicos': sitio['tipoSitiosTuristicos'],
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
    query_conditions.append({'nombreSitiosTuristicos': {'$regex': search_term, '$options': 'i'}, 'estadoSitiosTuristicos': '1'})

    sitios = db.SitiosTuristicos.find({'$or': query_conditions})

    lista_sitios = []
    for sitio in sitios:
        lista_sitios.append({
            '_id': str(sitio['_id']),
            'nombreSitiosTuristicos': sitio['nombreSitiosTuristicos'],
            'descripcionSitiosTuristicos': sitio['descripcionSitiosTuristicos'],
            'altitudSitiosTuristicos': sitio['altitudSitiosTuristicos'],
            'latitudSitiosTuristicos': sitio['latitudSitiosTuristicos'],
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
                'tipoSitiosTuristicos': data.get('tipoSitiosTuristicos', sitio['tipoSitiosTuristicos']),
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

#Reseñas
@app.route('/calificar', methods=['POST'])
def calificar():
    data = request.json

    usuario_id = ObjectId(data.get('usuario_id'))
    sitioturistico_id = ObjectId(data.get('sitioturistico_id'))
    calificacion = data.get('calificacion')
    comentario = data.get('comentario', '')  

    if not all([usuario_id, sitioturistico_id, calificacion]):
        return jsonify({'mensaje': 'Faltan datos obligatorios'}), 400

    calif = db.Calificacion.find_one({'usuario_id': usuario_id, 'sitioturistico_id': sitioturistico_id})

    if calif:
        return jsonify({'mensaje': 'El usuario no puede hacer más de un comentario en un sitio'}), 400

    try:
        calificacion_data = {
            "usuario_id": usuario_id,
            "sitioturistico_id": sitioturistico_id,
            "calificacion": calificacion,
            "comentario": comentario
        }
        db.Calificacion.insert_one(calificacion_data)

        return jsonify({'mensaje': 'Calificación registrada con éxito'}), 201

    except Exception as e:
        return jsonify({'mensaje': 'Error al registrar la calificación', 'error': str(e)}), 500

@app.route('/average-site-rating/<id>', methods=['GET'])
def calificaciones_count(id):

    if not id:
        return jsonify({'error': 'id es requerido'}), 400

    try:
        id = ObjectId(id)
    except Exception as e:
        return jsonify({'error': 'ID inválido'}), 400

    calificaciones_docs = db.Calificacion.find(
        {'sitioturistico_id': id},
        {'calificacion': 1, '_id': 0}
    )

    calificaciones_list = [int(doc['calificacion']) for doc in calificaciones_docs]


    sumStar = sum(calificaciones_list)
    count = len(calificaciones_list)
    if count == 0:
        count = 1
    prom = sumStar/count
    result = {
        'Promedio': prom
    }

    return jsonify(result)

@app.route('/calificaciones_sitio/<id>', methods=['GET'])
def obtener_calificaciones_por_sitio(id):

    if not id:
        return jsonify({"error": "Se requiere el ID del sitio turístico"}), 400

    try:
        calificaciones_docs = db.Calificacion.find(
            {'sitioturistico_id': ObjectId(id), 'comentario': {'$ne': ''}}
        ).limit(5)

        resultados = []
        for doc in calificaciones_docs:
            usuario = db.Usuarios.find_one({'_id': ObjectId(doc['usuario_id'])}, {'nombreUsuario': 1, '_id': 0})
            if usuario:
                resultados.append({
                    "nombreUsuario": usuario['nombreUsuario'],  
                    "calificacion": doc['calificacion'],
                    "comentario": doc.get('comentario', "Sin comentario")
                })

        return jsonify({"resultados": resultados}), 200

    except Exception as e:
        return jsonify({"error": str(e), "mensaje": "Error al procesar la solicitud"}), 500

@app.route('/deleteC/<id>', methods=['DELETE'])
def deleteC(id):
    if not ObjectId.is_valid(id):
        return jsonify({'mensaje': 'ID no válido'}), 400

    object_id = ObjectId(id)

    calificacion = db.Calificacion.find_one({'_id': object_id})

    if calificacion:
        db.Calificacion.delete_one({'_id': object_id})
        return jsonify({'mensaje': 'Calificacion eliminada exitosamente'}), 200
    else:
        return jsonify({'mensaje': 'No se encontraron calificaciones'}), 404

@app.route('/getC/<uid>/<lid>', methods=['GET'])
def getC(uid,lid):
    if not ObjectId.is_valid(uid) and ObjectId.is_valid(lid):
        return jsonify({'mensaje': 'ID no válido'}), 400

    user_id,local_id = ObjectId(uid),ObjectId(lid)

    calif = db.Calificacion.find_one({'usuario_id': user_id, 'sitioturistico_id': local_id})
    if calif:
        calif['_id'] = str(calif['_id'])
        calif['usuario_id'] = str(calif['usuario_id'])
        calif['sitioturistico_id'] = str(calif['sitioturistico_id'])
        return jsonify(calif), 200
    else:
        return jsonify({'mensaje': 'No se encontraron calificaciones'}), 404




#Start app
if __name__ == "__main__":
    app.run()