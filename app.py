import os
import json
import base64
import mysql.connector
import google.generativeai as genai
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# CHAVE API
api_key = os.getenv("GENAI_API_KEY")
if not api_key:
    raise ValueError("API key is not set in environment variables")

genai.configure(api_key=api_key)

# Conecta ao banco de dados
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",       
        user="root",            
        password="your_password", 
        database="consumption"  
    )

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        #Dados da requisição
        data = request.get_json()
        if 'image' not in data or 'meter_id' not in data:
            return jsonify({"error": "Image data or meter_id not provided"}), 400
        
        image_base64 = data['image']
        meter_id = data['meter_id']

        # Base64
        try:
            base64.b64decode(image_base64)
        except ValueError:
            return jsonify({"error": "Invalid base64 image data"}), 400

        # Verificar_mês atual
        if check_existing_reading(meter_id):
            return jsonify({"error": "Reading for this month already exists"}), 409
        
        #análise_image_LLM 
        prompt = f"""
        Extract the meter reading value from this image and return it as a JSON.
        Image data: {image_base64}
        """
        response = model.generate_content(prompt)
        response_text = response.text  # Supondo que a resposta tenha um atributo 'text'

        # Analise_resposta_LLM
        try:
            llm_response = json.loads(response_text)
        except json.JSONDecodeError:
            return jsonify({"error": "Failed to decode LLM response"}), 500
        
        
        meter_value = llm_response.get('meter_value')
        guid = llm_response.get('guid')

        #Salvar_banco_de_dados
        save_reading(meter_id, meter_value, guid)

        return jsonify({
            "temporary_link": "http://example.com/temp_link",
            "guid": guid,
            "meter_value": meter_value
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def check_existing_reading(meter_id):
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

  
    current_month = datetime.now().strftime("%Y-%m")

    
    query = """
    SELECT COUNT(*) as count FROM readings 
    WHERE meter_id = %s AND DATE_FORMAT(reading_date, '%%Y-%%m') = %s
    """
    cursor.execute(query, (meter_id, current_month))
    result = cursor.fetchone()
    conn.close()

    return result['count'] > 0

def save_reading(meter_id, meter_value, guid):
 
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO readings (meter_id, meter_value, guid, reading_date)
    VALUES (%s, %s, %s, NOW())
    """
    cursor.execute(query, (meter_id, meter_value, guid))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    app.run(debug=True)
