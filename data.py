from flask import Flask, request, jsonify
from flask_cors import CORS
import json

def buscar_categoria(nombre_categoria):
    tareas = leer_json('data.json')
    tareasfiltradas: dict = []
    try:
        for tarea in tareas["tasks"]:
            if tarea["category"] == nombre_categoria:
                tareasfiltradas.append(tarea)
        return tareasfiltradas
    except (FileNotFoundError, json.JSONDecodeError):
        return tareasfiltradas  # Retornar un diccionario vacío con "tasks" si no existe o está vacío
    
# Escribir datos en un archivo JSON
def escribir_json(nombre_archivo, datos):
    try:
        # Leer datos existentes
        datos_existentes = leer_json(nombre_archivo)
        if not isinstance(datos_existentes, dict) or "tasks" not in datos_existentes:
            # Si el archivo no contiene un diccionario con la clave "tasks", inicializarlo
            datos_existentes = {"tasks": []}
    except (FileNotFoundError, json.JSONDecodeError):
        datos_existentes = {"tasks": []}  # Si no existe el archivo o está vacío, inicializar como {"tasks": []}

    # Agregar nuevos datos
    if isinstance(datos, dict):
        datos_existentes["tasks"].append(datos) # Agregar el nuevo objeto a la lista "tasks"
    elif isinstance(datos, list):
        datos_existentes["tasks"].extend(datos)  # Agregar múltiples objetos si es una lista
    else:
        raise ValueError("Los datos deben ser un objeto o una lista de objetos.")

    # Escribir todos los datos
    with open(nombre_archivo, mode='w', encoding='utf-8') as file:
        json.dump(datos_existentes, file, ensure_ascii=False, indent=4)

# Leer datos de un archivo JSON
def leer_json(nombre_archivo):
    try:
        with open(nombre_archivo, mode='r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"tasks": []}  # Retornar un diccionario vacío con "tasks" si no existe o está vacío

def leer_categorias(nombre_archivo):
    try:
        datos_existentes = leer_json(nombre_archivo)
        if "categories" in datos_existentes:
            return datos_existentes["categories"]
        else:
            return []  # Retornar una lista vacía si no hay categorías
    except (FileNotFoundError, json.JSONDecodeError):
        return []  # Retornar una lista vacía si el archivo no existe o está vacío

def agregar_categoria(nombre_archivo, nueva_categoria):
    try:
        # Leer datos existentes
        datos_existentes = leer_json(nombre_archivo)
        if "categories" not in datos_existentes:
            datos_existentes["categories"] = []  # Inicializar la clave "categories" si no existe

        # Verificar si la categoría ya existe
        if any(categoria["name"] == nueva_categoria for categoria in datos_existentes["categories"]):
            return {"mensaje": "La categoría ya existe."}

        # Agregar la nueva categoría
        datos_existentes["categories"].append({"name": nueva_categoria})

        # Escribir los datos actualizados
        with open(nombre_archivo, mode='w', encoding='utf-8') as file:
            json.dump(datos_existentes, file, ensure_ascii=False, indent=4)

        return {"mensaje": "Categoría añadida exitosamente."}
    except (FileNotFoundError, json.JSONDecodeError):
        # Si el archivo no existe o está vacío, inicializarlo con la nueva categoría
        datos_existentes = {"tasks": [], "categories": [{"name": nueva_categoria}]}
        with open(nombre_archivo, mode='w', encoding='utf-8') as file:
            json.dump(datos_existentes, file, ensure_ascii=False, indent=4)
        return {"mensaje": "Categoría añadida exitosamente."}

def eliminar_tareajson(nombre_archivo, tarea_id):
    try:
        # Leer datos existentes
        datos_existentes = leer_json(nombre_archivo)
        if "tasks" in datos_existentes:
            # Filtrar las tareas para eliminar la que coincide con el id
            tareas_actualizadas = [tarea for tarea in datos_existentes["tasks"] if tarea["id"] != tarea_id]
            datos_existentes["tasks"] = tareas_actualizadas

            # Escribir los datos actualizados
            with open(nombre_archivo, mode='w', encoding='utf-8') as file:
                json.dump(datos_existentes, file, ensure_ascii=False, indent=4)

            return {"mensaje": "Tarea eliminada exitosamente."}
        else:
            return {"mensaje": "No se encontraron tareas."}
    except (FileNotFoundError, json.JSONDecodeError):
        return {"mensaje": "El archivo no existe o está vacío."}
    
def eliminar_categoriajson(nombre_archivo, categoria_nombre):
    try:
        # Leer datos existentes
        datos_existentes = leer_json(nombre_archivo)
        if "categories" in datos_existentes:
            # Filtrar las categorías para eliminar la que coincide con el nombre
            categorias_actualizadas = [categoria for categoria in datos_existentes["categories"] if categoria["name"] != categoria_nombre]
            datos_existentes["categories"] = categorias_actualizadas

            # Escribir los datos actualizados
            with open(nombre_archivo, mode='w', encoding='utf-8') as file:
                json.dump(datos_existentes, file, ensure_ascii=False, indent=4)

            return {"mensaje": "Categoría eliminada exitosamente."}
        else:
            return {"mensaje": "No se encontraron categorías."}
    except (FileNotFoundError, json.JSONDecodeError):
        return {"mensaje": "El archivo no existe o está vacío."}


app = Flask(__name__)
CORS(app)
@app.route('/guardar_json', methods=['POST'])
def guardar_json():
    datos = request.json.get('datos')
    escribir_json('data.json', datos)
    return jsonify({'mensaje': 'Datos guardados en JSON'})

@app.route('/leer_json', methods=['GET'])
def obtener_json():  # Renamed function
    datos = leer_json('data.json')  # No change here
    return jsonify(datos)

@app.route('/leer_categorias', methods=['GET'])
def obtener_categorias():
    categorias = leer_categorias('data.json')
    return jsonify(categorias)

@app.route('/agregar_categoria', methods=['POST'])
def nueva_categoria():
    # Obtener el nombre de la categoría directamente del cuerpo de la solicitud
    if request.is_json:
        nueva_categoria = request.get_json()  # Si es JSON, obtener el contenido directamente
    else:
        nueva_categoria = request.data.decode('utf-8')  # Si no es JSON, decodificar el cuerpo como texto

    if not nueva_categoria:
        return jsonify({'mensaje': 'La categoría es requerida.'}), 400

    resultado = agregar_categoria('data.json', nueva_categoria)
    return jsonify(resultado)

@app.route('/eliminar_tarea/<tarea_id>', methods=['DELETE'])
def eliminar_tarea(tarea_id):
    resultado = eliminar_tareajson('data.json', tarea_id)
    return jsonify(resultado)

@app.route('/eliminar_categoria/<categoria_nombre>', methods=['DELETE'])
def eliminar_categoria(categoria_nombre):
    resultado = eliminar_categoriajson('data.json', categoria_nombre)
    return jsonify(resultado)

@app.route('/buscar_categoria/<nombre_categoria>', methods=['GET'])
def buscar_categoria_route(nombre_categoria):
    tareas = buscar_categoria(nombre_categoria)
    return jsonify({"tasks": tareas})  # Envolver la lista en un diccionario

@app.route('/')
def home():
    return {"message": "API funcionando correctamente en Render!"}

if __name__ == '__main__':
    # Inicia la aplicación Flask
    app.run(host="0.0.0.0", port=5000)
