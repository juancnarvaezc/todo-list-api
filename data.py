from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import unicodedata

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

def unir_archivos_y_borrar(origen, destino):
    """Une el contenido de 'origen' al archivo 'destino' y elimina 'origen'."""
    archivo_origen = os.path.join(BASE_DIR, f"{origen}.json")
    archivo_destino = os.path.join(BASE_DIR, f"{destino}.json")

    inicializar_archivo(f"{origen}.json")
    inicializar_archivo(f"{destino}.json")

    datos_origen = leer_json(f"{origen}.json")
    datos_destino = leer_json(f"{destino}.json")

    # Combinar tareas y eliminar duplicados por ID
    tareas_origen = datos_origen.get("tasks", [])
    tareas_destino = datos_destino.get("tasks", [])
    tareas_combinadas = {t["id"]: t for t in tareas_destino}
    for t in tareas_origen:
        tareas_combinadas[t["id"]] = t
    datos_destino["tasks"] = list(tareas_combinadas.values())

    # Combinar categorías (evitar duplicados por nombre)
    categorias_origen = datos_origen.get("categories", [])
    categorias_destino = datos_destino.get("categories", [])
    nombres_categorias = {c["name"] for c in categorias_destino}
    for c in categorias_origen:
        if c["name"] not in nombres_categorias:
            categorias_destino.append(c)
            nombres_categorias.add(c["name"])
    datos_destino["categories"] = categorias_destino

    # Guardar datos combinados en el archivo destino
    with open(archivo_destino, 'w', encoding='utf-8') as f:
        json.dump(datos_destino, f, ensure_ascii=False, indent=4)

    # Eliminar archivo de origen
    if os.path.exists(archivo_origen):
        os.remove(archivo_origen)

    return {"mensaje": f"Archivo '{origen}.json' fusionado con '{destino}.json' y eliminado."}

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
    

def normalizar_texto(texto):
    """Normaliza texto: quita acentos, pasa a minúsculas y elimina caracteres especiales."""
    if not isinstance(texto, str):
        return ""
    texto = texto.strip()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = texto.lower()
    return texto

def capitalizar_categoria(texto):
    """Devuelve el texto con la primera letra en mayúscula y el resto en minúscula."""
    if not texto:
        return ""
    return texto.strip().capitalize()


def agregar_categoria(nombre_archivo, nueva_categoria):
    """Agrega una nueva categoría al archivo JSON evitando duplicados."""
    inicializar_archivo(nombre_archivo)
    ruta_archivo = os.path.join(BASE_DIR, nombre_archivo)
    try:
        datos_existentes = leer_json(nombre_archivo)
        if "categories" not in datos_existentes:
            datos_existentes["categories"] = []

        # Normaliza la nueva categoría para comparar
        nueva_categoria_normalizada = normalizar_texto(nueva_categoria)

        # Verifica duplicados considerando normalización
        for categoria in datos_existentes["categories"]:
            if normalizar_texto(categoria["name"]) == nueva_categoria_normalizada:
                return {"mensaje": "La categoría ya existe."}

        # Guarda la categoría con la primera letra en mayúscula
        categoria_final = capitalizar_categoria(nueva_categoria)
        datos_existentes["categories"].append({"name": categoria_final})

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

@app.route('/unir_archivos', methods=['POST'])
def unir_archivos():
    data = request.json
    origen = data.get("origen")  # sin ".json"
    destino = data.get("destino")  # sin ".json"
    
    if not origen or not destino:
        return jsonify({"mensaje": "Se requieren los campos 'origen' y 'destino'."}), 400

    if origen == destino:
        return jsonify({"mensaje": "Los archivos de origen y destino deben ser diferentes."}), 400

    resultado = unir_archivos_y_borrar(origen, destino)
    return jsonify(resultado)

@app.route('/')
def home():
    return {"message": "API de gestión de tareas y categorías"}

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
