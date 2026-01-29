from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import random
import os

app = Flask(__name__)
CORS(app)

# --- CORRECCIÓN AQUÍ ---
# Debe decir "PAYPHONE_TOKEN", no el token largo.
# El token largo lo pondremos luego en la configuración de Render.
TOKEN = os.environ.get("PAYPHONE_TOKEN", "")

@app.route('/', methods=['GET'])
def home():
    return "¡El servidor de Pagos ASINM está funcionando! 🚀"

@app.route('/crear-pago', methods=['POST'])
def crear_pago():
    if not TOKEN:
        return jsonify({"error": "Falta configurar el TOKEN en Render"}), 500

    url = "https://pay.payphonetodoesposible.com/api/Links"
    client_tx_id = f"WEB-{random.randint(100000, 999999)}"

    payload = {
        "amount": 100,           
        "amountWithoutTax": 100,
        "amountWithTax": 0,
        "tax": 0,
        "currency": "USD",
        "clientTransactionId": client_tx_id,
        "reference": "Compra Web ASINM",
        "expireIn": 60
    }

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json() if response.headers.get('Content-Type') == 'application/json' else response.text
            link = ""
            if isinstance(data, str):
                link = data.strip('"')
            elif isinstance(data, dict):
                link = data.get('payWithCard') or data.get('url')
            
            return jsonify({
                "message": "Link generado",
                "payment_url": link,
                "transaction_id": client_tx_id
            })
        else:
            return jsonify({"error": "PayPhone rechazó la solicitud", "detalle": response.text}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

