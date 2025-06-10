from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        raw_data = request.data.decode("utf-8")
        print("\n📥 Datos RAW recibidos:")
        print(raw_data)

        data = json.loads(raw_data)
        print("\n🔍 JSON interpretado:")
        print(json.dumps(data, indent=2))

        number = data["data"]["from"]
        message = data["data"]["body"]

        print(f"📩 Mensaje de {number}: {message}")
        return jsonify({"reply": f"✅ Recibido: {message}"})
    
    except Exception as e:
        print("❌ Error al procesar el webhook:", e)
        return jsonify({"reply": "❌ Error procesando datos del webhook."})

@app.route("/", methods=["GET"])
def index():
    return "✅ Webhook de prueba activo."

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


