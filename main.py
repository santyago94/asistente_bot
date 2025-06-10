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

    # Inicializar lista si no existe
    if number not in tasks:
        tasks[number] = []

    # Agregar tareas
    if message.startswith("agregar") or message.startswith("añadir"):
        lineas = message.split("\n")[1:]  # Ignorar la primera línea
        nuevas_tareas = [
            {
                "texto": linea.strip("•.- ").capitalize(),
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            for linea in lineas if linea.strip()
        ]
        tasks[number].extend(nuevas_tareas)
        respuesta = "📌 Tareas guardadas:\n" + "\n".join(
            f"- {t['texto']} ({t['fecha']})" for t in nuevas_tareas
        )

    # Ver tareas pendientes
    elif "ver" in message or "pendientes" in message:
        lista = tasks.get(number, [])
        if lista:
            respuesta = "📋 Tus tareas pendientes:\n" + "\n".join(
                f"{i+1}. {t['texto']} ({t['fecha']})" for i, t in enumerate(lista)
            )
        else:
            respuesta = "✅ No tienes tareas pendientes."

    # Finalizar una tarea específica
    elif message.startswith("finalizar") or message.startswith("borrar"):
        try:
            indice = int(message.split()[1]) - 1
            if 0 <= indice < len(tasks[number]):
                tarea = tasks[number].pop(indice)
                respuesta = f"✅ Tarea finalizada: {tarea['texto']}"
            else:
                respuesta = "⚠️ Número de tarea inválido."
        except (IndexError, ValueError):
            respuesta = "❌ Escribe *finalizar N* donde N es el número de la tarea."

    # Limpiar toda la lista
    elif "limpiar todo" in message:
        tasks[number] = []
        respuesta = "🧹 Todas las tareas han sido eliminadas."

    # Ayuda o mensaje por defecto
    else:
        nombre = nombres.get(number, number)
        respuesta = (
            f"👋 Hola {nombre}!\n"
            "Soy tu asistente de tareas. Comandos disponibles:\n"
            "- *agregar*:\n  agregar\n  - Comprar abono\n  - Regar plantas\n"
            "- *ver* o *pendientes*: Ver tus tareas con fechas\n"
            "- *finalizar N*: Eliminar una tarea específica\n"
            "- *limpiar todo*: Borrar todas las tareas"
        )

    # Guardar tareas actualizadas
    with open("tasks.json", "w") as f:
        json.dump(tasks, f)

    return jsonify({"reply": respuesta})


# Ruta de prueba para navegador
@app.route("/", methods=["GET"])
def index():
    return "✅ Bot activo y escuchando mensajes."


# Ruta para monitoreo
@app.route("/ping", methods=["GET"])
def ping():
    return "🚀 Bot corriendo correctamente."


# Panel de administración web
@app.route("/admin")
def admin():
    html = """
    <h2>📋 Tareas Pendientes por Usuario</h2>
    {% for num, lista in tasks.items() %}
        <h4>{{ nombres.get(num, num) }}:</h4>
        <ul>
        {% for tarea in lista %}
            <li>{{ tarea['texto'] }} ({{ tarea['fecha'] }})</li>
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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


