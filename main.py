from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("🔔 Webhook recibido:", data)  # <- Esto te muestra si el mensaje llegó

    try:
        number = data["data"]["from"]
        message = data["data"]["body"]
        print(f"📩 Mensaje de {number}: {message}")

        # Responder con un eco
        return jsonify({"reply": f"✅ Recibido: {message}"})
    except Exception as e:
        print("❌ Error procesando:", e)
        return jsonify({"reply": "❌ Formato de mensaje inválido."})

@app.route("/", methods=["GET"])
def index():
    return "🔧 Webhook de prueba activo."

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

