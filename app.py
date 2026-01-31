from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import random
import os

app = Flask(__name__)
CORS(app)

TOKEN = os.environ.get("PAYPHONE_TOKEN", "")
STORE_ID = os.environ.get("PAYPHONE_STORE_ID", "")  # Agregar StoreID

@app.route('/', methods=['GET'])
def home():
    return "¡El servidor de Pagos ASINM está funcionando! 🚀"

@app.route('/crear-pago', methods=['POST'])
def crear_pago():
    if not TOKEN:
        return jsonify({"error": "Falta configurar el TOKEN en Render"}), 500
    
    if not STORE_ID:
        return jsonify({"error": "Falta configurar el STORE_ID en Render"}), 500

    # Recibir datos del frontend
    data = request.get_json()
    
    # Obtener el monto en dólares
    amount_usd = data.get('amount', 1.00)
    phone_number = data.get('phoneNumber', '')
    country_code = data.get('countryCode', '593')
    
    # Validar teléfono
    if not phone_number:
        return jsonify({"error": "Número de teléfono requerido"}), 400
    
    # Validar monto
    try:
        amount_usd = float(amount_usd)
        if amount_usd <= 0:
            return jsonify({"error": "El monto debe ser mayor a 0"}), 400
        if amount_usd > 10000:
            return jsonify({"error": "El monto excede el límite permitido"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Monto inválido"}), 400
    
    # IMPORTANTE: Convertir a centavos (PayPhone requiere centavos)
    amount_cents = int(amount_usd * 100)
    
    # URL para API Sale (cobro directo a la app)
    url = "https://pay.payphonetodoesposible.com/api/Sale"
    client_tx_id = f"ASINM-{random.randint(100000, 999999)}"

    # Payload según documentación PayPhone API Sale
    payload = {
        "phoneNumber": phone_number,
        "countryCode": country_code,
        "amount": amount_cents,           # Monto total en centavos
        "amountWithoutTax": amount_cents, # Sin impuestos
        "amountWithTax": 0,
        "tax": 0,
        "currency": "USD",
        "clientTransactionId": client_tx_id,
        "storeId": STORE_ID,
        "reference": data.get('reference', f'Pago ASINM ${amount_usd:.2f}')
    }

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            response_data = response.json()
            
            return jsonify({
                "success": True,
                "message": "Solicitud de pago enviada",
                "transaction_id": response_data.get('transactionId'),
                "client_transaction_id": client_tx_id,
                "amount": amount_usd,
                "phone_number": phone_number
            })
        else:
            error_data = response.json() if response.headers.get('Content-Type') == 'application/json' else response.text
            return jsonify({
                "error": "PayPhone rechazó la solicitud", 
                "detalle": error_data
            }), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint para consultar estado de transacción
@app.route('/consultar-pago/<transaction_id>', methods=['GET'])
def consultar_pago(transaction_id):
    if not TOKEN:
        return jsonify({"error": "Falta configurar el TOKEN"}), 500
    
    url = f"https://pay.payphonetodoesposible.com/api/Sale/{transaction_id}"
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": "No se pudo consultar la transacción"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
