from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import random
import os

app = Flask(__name__)
# Permitir que tu página web (React/HTML) haga peticiones a este servidor
CORS(app)

# --- CREDENCIALES (Las configuraremos en Render) ---
# Si no encuentra la variable, usará una cadena vacía (y fallará seguro)
TOKEN = os.environ.get("sOExDWeM9P9E6vF04bpAx_A5XT1SGTofw2ozc-pMQJbAr1B46MPuk2nv-vW6KE5Ra75fEJSeLTVkZ8BI2K9op4nv52YJJ8IELyRBENX1YHZ7SEqqglcy8Z85o_asJrdRSF466wpMjoIcNSWgHH0abx4WmQuushnFg-RYwxUjg64TVLu-zaUm7cxAQAHj7H-SEOmZb3ndasza0JEmV0-5Y4JCRWiuwIeqyKzasGVR0FmVBKqu_30fYUP0hOa853qgcIwGMpT6ukYiNgTY0Lci0GGegDby-dasE5-1vCBt0A_-_F733NbC0Ft3jaNaB63VPeoEsw", "")

@app.route('/', methods=['GET'])
def home():
    return "¡El servidor de Pagos ASINM está funcionando! 🚀"

@app.route('/crear-pago', methods=['POST'])
def crear_pago():
    """Genera un link de pago bajo demanda"""
    
    # 1. Validar Token
    if not TOKEN:
        return jsonify({"error": "Falta configurar el TOKEN en Render"}), 500

    url = "https://pay.payphonetodoesposible.com/api/Links"
    
    # 2. Generar ID único corto
    client_tx_id = f"WEB-{random.randint(100000, 999999)}"

    # 3. Datos del cobro (Podrías recibirlos desde el frontend si quisieras)
    # Por ahora lo dejamos fijo en $1.00 como pediste
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
        # 4. Conectar con PayPhone
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            # Intentar sacar el link
            data = response.json() if response.headers.get('Content-Type') == 'application/json' else response.text
            
            # Manejo robusto de la respuesta de PayPhone
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
    # Esto es para probar localmente, en Render se usará Gunicorn
    app.run(debug=True)