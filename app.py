from flask import Flask, render_template, request, jsonify
import os
import xmlrpc.client
import ssl
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__, template_folder='.')

# Configuración desde variables de entorno
app.config['SECRET_KEY'] = 'f4e887491361873f4555836571a012466eb9abb6'  # Tu clave secreta

def conectar_odoo():
    """Conexión segura a la API de Odoo con manejo mejorado de errores"""
    try:
        # Configuración SSL
        ssl_context = ssl._create_unverified_context() if os.getenv('ODOO_URL', '').startswith('https') else None
        
        # Conexión común
        common = xmlrpc.client.ServerProxy(
            f'{os.getenv("ODOO_URL")}/xmlrpc/2/common',
            context=ssl_context,
            allow_none=True
        )
        
        # Autenticación
        uid = common.authenticate(
            os.getenv("ODOO_DB"),
            os.getenv("ODOO_USER"),
            os.getenv("ODOO_PASSWORD"),
            {}
        )
        
        if not uid:
            raise ConnectionError("Autenticación fallida con Odoo")
        
        # Conexión a modelos
        models = xmlrpc.client.ServerProxy(
            f'{os.getenv("ODOO_URL")}/xmlrpc/2/object',
            context=ssl_context,
            allow_none=True
        )
        
        return uid, models
        
    except xmlrpc.client.Fault as e:
        app.logger.error(f"Error XML-RPC: {str(e)}")
        raise
    except Exception as e:
        app.logger.error(f"Error de conexión con Odoo: {str(e)}")
        raise

@app.route('/')
def index():
    return render_template('formulario.html')

@app.route('/procesar', methods=['POST'])
def procesar_formulario():
    try:
        # Validación de datos
        required_fields = {
            'vorname': 'Vorname',
            'nachname': 'Nachname',
            'email': 'E-Mail',
            'geburtsdatum': 'Geburtsdatum',
            'strasse': 'Straße',
            'postleitzahl': 'Postleitzahl',
            'ort': 'Ort',
            'tipo_aseguradora': 'Krankenversicherung',
            'es_beamter': 'Beamter Status',
            'tipo_seguro': 'Versicherungsart',
            'numero_seguro': 'Versicherungsnummer'
        }
        
        # Verificar campos requeridos
        missing_fields = []
        for field, name in required_fields.items():
            if not request.form.get(field):
                missing_fields.append(name)
        
        if missing_fields:
            return jsonify({
                'status': 'error',
                'message': 'Pflichtfelder fehlen',
                'missing_fields': missing_fields
            }), 400

        # Procesamiento de fechas
        geburtsdatum = request.form.get('geburtsdatum')
        if geburtsdatum:
            try:
                geburtsdatum = datetime.strptime(geburtsdatum, '%Y-%m-%d').strftime('%Y-%m-%d')
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Ungültiges Datumsformat (verwenden Sie YYYY-MM-DD)'
                }), 400

        # Procesamiento de campos especiales
        es_beamter = request.form.get('es_beamter') == 'Ja'
        tipo_seguro = request.form.get('tipo_seguro')
        anrede = request.form.get('anrede')

        # Mapeo a campos de Odoo
        datos_odoo = {
            'x_anrede': anrede,
            'x_versicherung_typ': request.form.get('tipo_aseguradora'),
            'x_beamter': es_beamter,
            'x_andere': tipo_seguro,
            'x_versicherung_nummer': request.form.get('numero_seguro'),
            'x_titel': request.form.get('titulo'),
            'x_vorname': request.form.get('vorname'),
            'x_nachname': request.form.get('nachname'),
            'x_geburtsdatum': geburtsdatum,
            'x_strasse': request.form.get('strasse'),
            'x_plz': request.form.get('postleitzahl'),
            'x_ort': request.form.get('ort'),
            'x_email': request.form.get('email'),
            'x_telefon_mobil': request.form.get('telefon_mobil'),
            'x_telefon_festnetz': request.form.get('telefon_festnetz'),
        }

        # Conexión con Odoo
        uid, models = conectar_odoo()
        paciente_id = models.execute_kw(
            os.getenv("ODOO_DB"), uid, os.getenv("ODOO_PASSWORD"),
            'psicoterapia.paciente', 'create',
            [datos_odoo]
        )

        return jsonify({
            'status': 'success',
            'message': 'Daten erfolgreich in Odoo gespeichert',
            'odoo_id': paciente_id,
            'data': {
                'name': f"{anrede} {datos_odoo['x_vorname']} {datos_odoo['x_nachname']}",
                'email': datos_odoo['x_email']
            }
        })

    except xmlrpc.client.Fault as e:
        return jsonify({
            'status': 'error',
            'message': 'Fehler bei der Kommunikation mit Odoo',
            'system_message': str(e)
        }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Interner Serverfehler',
            'system_message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', '10000')),
        debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    )
