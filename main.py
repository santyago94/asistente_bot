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
        lineas = message.split("\n")[1:]
        nuevas_tareas = [
            {
                "texto": linea.strip("•.- ").capitalize(),
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            for linea in lineas if linea.strip()
        ]
        tasks[number].extend(nuevas_tareas)
        respuesta = "📌 Tareas actualizadas:\n" + "\n".join(
            f"{i+1}. {t['texto']} ({t['fecha']})" for i, t in enumerate(tasks[number])
        )

    # Finalizar tarea específica
    elif message.startswith("finalizar"):
        try:
            indice = int(message.split()[1]) - 1
            if 0 <= indice < len(tasks[number]):
                tarea = tasks[number].pop(indice)
                respuesta = f"✅ Tarea finalizada: {tarea['texto']}\n\n📋 Lista actual:\n"
                respuesta += "\n".join(
                    f"{i+1}. {t['texto']} ({t['fecha']})" for i, t in enumerate(tasks[number])
                ) if tasks[number] else "✅ No tienes tareas pendientes."
            else:
                respuesta = "⚠️ Número de tarea inválido."
        except (IndexError, ValueError):
            respuesta = "❌ Escribe *finalizar N* donde N es el número de la tarea."

    # Registrar nombre si no está registrado
    elif number not in nombres:
        if message.startswith("mi nombre es"):
            posible_nombre = message.replace("mi nombre es", "").strip().capitalize()
            if posible_nombre:
                nombres[number] = posible_nombre
                with open("nombres.json", "w") as f:
                    json.dump(nombres, f)
                respuesta = (
                    f"✅ Gracias, {posible_nombre}. ¡Tu nombre ha sido registrado!\n\n"
                    "Ahora puedes agregar tareas así:\n"
                    "*agregar*\n- Comprar abono\n- Limpiar pozo"
                )
            else:
                respuesta = "❌ No entendí tu nombre. Por favor escribe: *mi nombre es Adonay*"
        else:
            respuesta = (
                "👋 Hola, antes de comenzar necesito saber tu nombre.\n"
                "Por favor escribe: *mi nombre es Adonay*"
            )

    # Mostrar menú si ya está registrado
    else:
        nombre = nombres[number]
        respuesta = (
            f"👋 Hola {nombre}!\n"
            "Puedes escribirme así para agregar tareas:\n"
            "*agregar*\n- Comprar abono\n- Limpiar pozo\n\n"
            "Y para finalizar alguna:\n"
            "*finalizar 1*"
        )

    # Guardar tareas actualizadas
    with open("tasks.json", "w") as f:
        json.dump(tasks, f)

    return jsonify({"reply": respuesta})


@app.route("/", methods=["GET"])
def index():
    return "✅ Bot activo y escuchando mensajes."


@app.route("/ping", methods=["GET"])
def ping():
    return "🚀 Bot corriendo correctamente."


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
