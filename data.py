from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

# Ruta base para la carpeta "data"
BASE_DIR = os.path.join(os.getcwd(), "data")

def inicializar_carpeta():
    """Crea la carpeta 'data' si no existe."""
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)

def inicializar_archivo(nombre_archivo):
    """Crea un archivo JSON con la estructura inicial si no existe."""
    inicializar_carpeta()
    ruta_archivo = os.path.join(BASE_DIR, nombre_archivo)
    if not os.path.exists(ruta_archivo):
        with open(ruta_archivo, mode='w', encoding='utf-8') as file:
            json.dump({
                "tasks": [], 
                "categories": [
                    {"name": "General"},
                    {"name": "Trabajo"},
                    {"name": "Personal"}
                ]
            }, file, ensure_ascii=False, indent=4)
def leer_json(nombre_archivo):
    """Lee datos de un archivo JSON."""
    inicializar_archivo(nombre_archivo)
    ruta_archivo = os.path.join(BASE_DIR, nombre_archivo)
    try:
        with open(ruta_archivo, mode='r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"tasks": [], "categories": []}

def escribir_json(nombre_archivo, datos):
    """Escribe datos en un archivo JSON."""
    inicializar_archivo(nombre_archivo)
    ruta_archivo = os.path.join(BASE_DIR, nombre_archivo)
    try:
        datos_existentes = leer_json(nombre_archivo)
        if not isinstance(datos_existentes, dict) or "tasks" not in datos_existentes:
            datos_existentes = {"tasks": []}

        if isinstance(datos, dict):
            datos_existentes["tasks"].append(datos)
        elif isinstance(datos, list):
            datos_existentes["tasks"].extend(datos)
        else:
            raise ValueError("Los datos deben ser un objeto o una lista de objetos.")

        with open(ruta_archivo, mode='w', encoding='utf-8') as file:
            json.dump(datos_existentes, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error al escribir en el archivo JSON: {e}")

def buscar_categoria(nombre_archivo, nombre_categoria):
    """Busca tareas por categoría."""
    tareas = leer_json(nombre_archivo)
    tareasfiltradas = []
    try:
        for tarea in tareas["tasks"]:
            if tarea["category"] == nombre_categoria:
                tareasfiltradas.append(tarea)
        return tareasfiltradas
    except KeyError:
        return []

def agregar_categoria(nombre_archivo, nueva_categoria):
    """Agrega una nueva categoría al archivo JSON."""
    inicializar_archivo(nombre_archivo)
    ruta_archivo = os.path.join(BASE_DIR, nombre_archivo)
    try:
        datos_existentes = leer_json(nombre_archivo)
        if "categories" not in datos_existentes:
            datos_existentes["categories"] = []

        if any(categoria["name"] == nueva_categoria for categoria in datos_existentes["categories"]):
            return {"mensaje": "La categoría ya existe."}

        datos_existentes["categories"].append({"name": nueva_categoria})

        with open(ruta_archivo, mode='w', encoding='utf-8') as file:
            json.dump(datos_existentes, file, ensure_ascii=False, indent=4)

        return {"mensaje": "Categoría añadida exitosamente."}
    except Exception as e:
        return {"mensaje": f"Error al agregar la categoría: {e}"}

def eliminar_tareajson(nombre_archivo, tarea_id):
    """Elimina una tarea por ID."""
    inicializar_archivo(nombre_archivo)
    ruta_archivo = os.path.join(BASE_DIR, nombre_archivo)
    try:
        datos_existentes = leer_json(nombre_archivo)
        if "tasks" in datos_existentes:
            tareas_actualizadas = [tarea for tarea in datos_existentes["tasks"] if tarea["id"] != tarea_id]
            datos_existentes["tasks"] = tareas_actualizadas

            with open(ruta_archivo, mode='w', encoding='utf-8') as file:
                json.dump(datos_existentes, file, ensure_ascii=False, indent=4)

            return {"mensaje": "Tarea eliminada exitosamente."}
        else:
            return {"mensaje": "No se encontraron tareas."}
    except Exception as e:
        return {"mensaje": f"Error al eliminar la tarea: {e}"}

def eliminar_categoriajson(nombre_archivo, categoria_nombre):
    """Elimina una categoría por nombre."""
    inicializar_archivo(nombre_archivo)
    ruta_archivo = os.path.join(BASE_DIR, nombre_archivo)
    try:
        datos_existentes = leer_json(nombre_archivo)
        if "categories" in datos_existentes:
            categorias_actualizadas = [categoria for categoria in datos_existentes["categories"] if categoria["name"] != categoria_nombre]
            datos_existentes["categories"] = categorias_actualizadas

            with open(ruta_archivo, mode='w', encoding='utf-8') as file:
                json.dump(datos_existentes, file, ensure_ascii=False, indent=4)

            return {"mensaje": "Categoría eliminada exitosamente."}
        else:
            return {"mensaje": "No se encontraron categorías."}
    except Exception as e:
        return {"mensaje": f"Error al eliminar la categoría: {e}"}

app = Flask(__name__)
CORS(app)

@app.route('/guardar_json/<uuid>', methods=['POST'])
def guardar_json(uuid):
    nombre_archivo = f"{uuid}.json"
    datos = request.json.get('datos')
    escribir_json(nombre_archivo, datos)
    return jsonify({'mensaje': 'Datos guardados en JSON'})

@app.route('/leer_json/<uuid>', methods=['GET'])
def obtener_json(uuid):
    nombre_archivo = f"{uuid}.json"
    datos = leer_json(nombre_archivo)
    return jsonify(datos)

@app.route('/leer_categorias/<uuid>', methods=['GET'])
def obtener_categorias(uuid):
    nombre_archivo = f"{uuid}.json"
    categorias = leer_json(nombre_archivo).get("categories", [])
    return jsonify(categorias)

@app.route('/agregar_categoria/<uuid>', methods=['POST'])
def nueva_categoria(uuid):
    nombre_archivo = f"{uuid}.json"
    nueva_categoria = request.json.get("name")
    if not nueva_categoria:
        return jsonify({'mensaje': 'La categoría es requerida.'}), 400

    resultado = agregar_categoria(nombre_archivo, nueva_categoria)
    return jsonify(resultado)

@app.route('/eliminar_tarea/<uuid>/<tarea_id>', methods=['DELETE'])
def eliminar_tarea(uuid, tarea_id):
    nombre_archivo = f"{uuid}.json"
    resultado = eliminar_tareajson(nombre_archivo, tarea_id)
    return jsonify(resultado)

@app.route('/eliminar_categoria/<uuid>/<categoria_nombre>', methods=['DELETE'])
def eliminar_categoria(uuid, categoria_nombre):
    nombre_archivo = f"{uuid}.json"
    resultado = eliminar_categoriajson(nombre_archivo, categoria_nombre)
    return jsonify(resultado)

@app.route('/buscar_categoria/<uuid>/<nombre_categoria>', methods=['GET'])
def buscar_categoria_route(uuid, nombre_categoria):
    nombre_archivo = f"{uuid}.json"
    tareas = buscar_categoria(nombre_archivo, nombre_categoria)
    return jsonify({"tasks": tareas})

@app.route('/')
def home():
    return {"message": "API funcionando correctamente en Render!"}

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
