# app.py
from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__, template_folder='.') 

# Configuración básica
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Ruta principal que muestra el formulario
@app.route('/')
def index():
    return render_template('index.html')  # Si tu archivo se llama index.html

# Ruta para procesar el formulario
@app.route('/procesar', methods=['POST'])
def procesar_formulario():
    try:
        # Recoger datos del formulario
        datos = {
            'tipo_aseguradora': request.form.get('tipo_aseguradora'),
            'es_beamter': request.form.get('es_beamter'),
            'tipo_seguro': request.form.get('tipo_seguro'),
            'numero_seguro': request.form.get('numero_seguro'),
            'anrede': request.form.get('anrede'),
            'titulo': request.form.get('titulo'),
            'vorname': request.form.get('vorname'),
            'nachname': request.form.get('nachname'),
            'geburtsdatum': request.form.get('geburtsdatum'),
            'strasse': request.form.get('strasse'),
            'postleitzahl': request.form.get('postleitzahl'),
            'ort': request.form.get('ort'),
            'email': request.form.get('email'),
            'telefon_mobil': request.form.get('telefon_mobil'),
            'telefon_festnetz': request.form.get('telefon_festnetz'),
            'fecha_registro': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Aquí deberías:
        # 1. Validar los datos
        # 2. Guardar en base de datos
        # 3. Integrar con Odoo (usando XML-RPC o REST API)
        
        return jsonify({
            'status': 'success',
            'message': 'Formulario recibido correctamente',
            'data': datos
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)