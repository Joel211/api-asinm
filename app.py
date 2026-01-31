from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import random
import os

app = Flask(__name__)
CORS(app)

TOKEN = os.environ.get("PAYPHONE_TOKEN", "")

@app.route('/', methods=['GET'])
def home():
    return "¡El servidor de Pagos ASINM está funcionando! 🚀"

@app.route('/crear-pago', methods=['POST'])
def crear_pago():
    if not TOKEN:
        return jsonify({"error": "Falta configurar el TOKEN en Render"}), 500

    # Recibir datos del frontend
    data = request.get_json()
    
    # Obtener el monto en dólares (por defecto 1.00)
    amount_usd = data.get('amount', 1.00)
    
    # Validar monto
    try:
        amount_usd = float(amount_usd)
        if amount_usd <= 0:
            return jsonify({"error": "El monto debe ser mayor a 0"}), 400
        if amount_usd > 10000:
            return jsonify({"error": "El monto excede el límite permitido"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Monto inválido"}), 400
    
    # Convertir a centavos (PayPhone trabaja en centavos)
    amount_cents = int(amount_usd * 100)

    url = "https://pay.payphonetodoesposible.com/api/Links"
    client_tx_id = f"ASINM-{random.randint(100000, 999999)}"

    payload = {
        "amount": amount_cents,
        "amountWithoutTax": amount_cents,
        "amountWithTax": 0,
        "tax": 0,
        "currency": "USD",
        "clientTransactionId": client_tx_id,
        "reference": data.get('reference', f'Membresía ASINM ${amount_usd:.2f}'),
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
                "success": True,
                "message": "Link generado",
                "payment_url": link,
                "transaction_id": client_tx_id,
                "amount": amount_usd
            })
        else:
            return jsonify({"error": "PayPhone rechazó la solicitud", "detalle": response.text}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)


