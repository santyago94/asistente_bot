from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)

    print("\n🔔 Webhook recibido COMPLETO:")
    print(json.dumps(data, indent=2))  # ← Esto imprimirá todo el contenido bien formateado

    # Intentamos responder con los datos básicos si existen
    try:
        number = data["data"]["from"]
        message = data["data"]["body"]
        print(f"📩 Mensaje de {number}: {message}")
        return jsonify({"reply": f"✅ Recibido: {message}"})
    except Exception as e:
        print("❌ Error leyendo mensaje:", e)
        return jsonify({"reply": "❌ Formato de mensaje inválido."})

@app.route("/", methods=["GET"])
def index():
    return "✅ Webhook de prueba activo."

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

