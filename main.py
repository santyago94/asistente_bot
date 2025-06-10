from flask import Flask, request, jsonify, render_template_string
import json
import os
from datetime import datetime

app = Flask(__name__)

# Cargar tareas desde archivo JSON
if os.path.exists("tasks.json"):
    with open("tasks.json", "r") as f:
        tasks = json.load(f)
else:
    tasks = {}

# Cargar nombres personalizados
if os.path.exists("nombres.json"):
    with open("nombres.json", "r") as f:
        nombres = json.load(f)
else:
    nombres = {}

# Ruta para recibir mensajes de WhatsApp desde UltraMsg
@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    data = request.get_json()

    try:
        number = data["data"]["from"]
        message = data["data"]["body"].strip().lower()
    except (KeyError, TypeError):
        return jsonify({"reply": "❌ Formato de mensaje inválido."})

    respuesta = ""

    # Añadir tareas
    if message.startswith("agregar") or message.startswith("añadir"):
        lineas = message.split("\n")[1:]  # Ignorar la primera línea
        tareas = [
        linea.strip("•.- ").capitalize() for linea in lineas if linea.strip()
        ]
        if number not in tasks:
            tasks[number] = []
        tasks[number].extend(tareas)
        respuesta = f"📌 Tareas guardadas:\n- " + "\n- ".join(tareas)

    # Ver tareas pendientes
    elif "ver" in message or "pendientes" in message:
        lista = tasks.get(number, [])
        if lista:
            respuesta = "📋 Tienes las siguientes tareas pendientes:\n- " + "\n- ".join(lista)
        else:
            respuesta = "✅ No tienes tareas pendientes."

    # Limpiar tareas
    elif "limpiar" in message or "borrar" in message:
        tasks[number] = []
        respuesta = "🧹 Tareas eliminadas."

    # Mensaje por defecto / ayuda
    else:
        nombre = nombres.get(number, number)
        respuesta = (
            f"👋 Hola {nombre}!\n"
            "Soy tu asistente de tareas. Puedes usar los siguientes comandos:\n"
            "- *agregar* o *añadir*: para registrar tareas\n"
            "- *ver* o *pendientes*: para consultar tus tareas\n"
            "- *limpiar* o *borrar*: para eliminar todas las tareas"
        )

    # Guardar las tareas en el archivo
    with open("tasks.json", "w") as f:
        json.dump(tasks, f)

    return jsonify({"reply": respuesta})


# Ruta de prueba para navegador y UptimeRobot
@app.route("/", methods=["GET"])
def index():
    return "✅ Bot activo y escuchando mensajes."


# Ruta ping de test adicional
@app.route("/ping", methods=["GET"])
def ping():
    return "🚀 Bot corriendo correctamente."


# Panel de administración
@app.route("/admin")
def admin():
    html = """
    <h2>📋 Tareas Pendientes por Usuario</h2>
    {% for num, lista in tasks.items() %}
        <h4>{{ nombres.get(num, num) }}:</h4>
        <ul>
        {% for tarea in lista %}
            <li>{{ tarea }}</li>
        {% endfor %}
        </ul>
    {% endfor %}

    <hr>
    <h2>📞 Usuarios Registrados</h2>
    <ul>
    {% for num, nom in nombres.items() %}
        <li><b>{{ nom }}</b>: {{ num }}</li>
    {% endfor %}
    </ul>
    """
    return render_template_string(html, tasks=tasks, nombres=nombres)


# Ejecutar el servidor en Replit o entorno local
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
