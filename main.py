from flask import Flask, request, jsonify
import json
import os
from datetime import datetime
import requests

app = Flask(__name__)

# TOKEN de UltraMsg (mejor usar variables de entorno)
ULTRAMSG_TOKEN = os.getenv("ULTRAMSG_TOKEN") or "a7y668viie06mzh9"  # Reemplaza si no usas .env
INSTANCE_ID = "instance124726"

# Cargar tareas desde archivo JSON
if os.path.exists("tasks.json"):
    with open("tasks.json", "r") as f:
        tasks = json.load(f)
else:
    tasks = {}

# Cargar nombres personalizados desde nombres.json
if os.path.exists("nombres.json"):
    with open("nombres.json", "r") as f:
        nombres = json.load(f)
else:
    nombres = {}

# Función para enviar mensaje por UltraMsg
def enviar_mensaje(numero, mensaje):
    url = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/chat"
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": numero,
        "body": mensaje
    }
    headers = {"Content-Type": "application/json"}
    try:
        requests.post(url, json=payload, headers=headers)
    except Exception as e:
        print(f"Error al enviar mensaje a {numero}: {e}")

# Ruta principal del bot (Webhook)
@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    data = request.get_json()

    try:
        number = data["data"]["from"]
        message = data["data"]["body"].strip().lower()
    except (KeyError, TypeError):
        return jsonify({"reply": "❌ Formato de mensaje inválido."})

    respuesta = ""

    if "agregar" in message or "añadir" in message:
        lineas = message.split("\n")
        tareas = [linea.strip("•.- ").capitalize() for linea in lineas if linea.strip()]
        if number not in tasks:
            tasks[number] = []
        tasks[number].extend(tareas)
        respuesta = f"📌 Tareas guardadas:\n- " + "\n- ".join(tareas)

    elif "ver" in message or "pendientes" in message:
        lista = tasks.get(number, [])
        if lista:
            respuesta = "📋 Tienes las siguientes tareas pendientes:\n- " + "\n- ".join(lista)
        else:
            respuesta = "✅ No tienes tareas pendientes."

    elif "limpiar" in message or "borrar" in message:
        tasks[number] = []
        respuesta = "🧹 Tareas eliminadas."

    else:
        nombre = nombres.get(number, number)
        respuesta = (
            f"👋 Hola {nombre}!\n"
            "Soy tu asistente de tareas. Puedes usar los siguientes comandos:\n"
            "- *agregar* o *añadir*: para registrar tareas\n"
            "- *ver* o *pendientes*: para consultar tus tareas\n"
            "- *limpiar* o *borrar*: para eliminarlas todas"
        )

    # Guardar cambios
    with open("tasks.json", "w") as f:
        json.dump(tasks, f, indent=2)

    return jsonify({"reply": respuesta})

# Ruta para probar el bot
@app.route("/", methods=["GET"])
def home():
    return "Bot de tareas funcionando correctamente ✅"

# Ruta de recordatorio diario
@app.route("/recordatorio", methods=["GET"])
def enviar_recordatorios():
    enviados = 0
    for numero, lista in tasks.items():
        if lista:
            mensaje = "🔔 *Recordatorio diario*\nEstas son tus tareas pendientes:\n- " + "\n- ".join(lista)
            enviar_mensaje(numero, mensaje)
            enviados += 1
    return f"✅ Recordatorios enviados a {enviados} usuarios.", 200

# Ejecutar localmente si no se usa gunicorn
if __name__ == "__main__":
    app.run(debug=True)
