from flask import Flask, redirect, request, render_template_string
import random
import csv
from pathlib import Path
from urllib.parse import urlparse

app = Flask(__name__)

# Configuración
CSV_FILE = 'url_database.csv'
BASE_DOMAIN = "http://localhost:5000"  # HTTP para desarrollo local

# Crear archivo CSV si no existe
def init_csv():
    if not Path(CSV_FILE).exists():
        with open(CSV_FILE, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['hash_code', 'long_url'])

# Cargar URLs desde CSV
def load_urls():
    urls = {}
    if Path(CSV_FILE).exists():
        with open(CSV_FILE, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                urls[row['hash_code']] = row['long_url']
    return urls

# Guardar nueva URL en CSV
def save_url(hash_code, long_url):
    with open(CSV_FILE, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([hash_code, long_url])

# Generar hash único de 4 dígitos
def generate_unique_hash():
    urls = load_urls()
    while True:
        hash_code = str(random.randint(1000, 9999))
        if hash_code not in urls:
            return hash_code

# Inicializar CSV al iniciar
init_csv()

# Plantilla HTML (igual que antes)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔗 Acortador de URLs</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f8f9fa;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .container {
            max-width: 600px;
            margin-top: 50px;
        }
        .card {
            border-radius: 15px;
            box-shadow: 0 6px 10px rgba(0, 0, 0, 0.1);
        }
        .card-header {
            background-color: #0d6efd;
            color: white;
            border-radius: 15px 15px 0 0 !important;
        }
        .btn-primary {
            background-color: #0d6efd;
            border: none;
        }
        .result-box {
            background-color: #e9ecef;
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
        }
        .version-footer {
            text-align: center;
            margin-top: 20px;
            color: #6c757d;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="card-header text-center">
                <h1>🔗 Acortador de URLs</h1>
            </div>
            <div class="card-body">
                <form action="/shorten" method="post">
                    <div class="mb-3">
                        <input type="url" class="form-control form-control-lg" name="url" placeholder="https://ejemplo.com" required>
                    </div>
                    <button type="submit" class="btn btn-primary btn-lg w-100">Acortar URL</button>
                </form>

                {% if short_url %}
                <div class="result-box mt-4">
                    <h5 class="text-success">✅ URL acortada:</h5>
                    <div class="input-group mb-3">
                        <input id="short-url" type="text" class="form-control" value="{{ short_url }}" readonly>
                        <button class="btn btn-outline-secondary" onclick="copyToClipboard()">Copiar</button>
                    </div>
                    <a href="{{ short_url }}" target="_blank" class="btn btn-success w-100">Probar enlace</a>
                </div>
                {% endif %}
            </div>
        </div>
        <div class="version-footer">
            Versión 2.0 - Persistente y sin errores HTTPS
        </div>
    </div>

    <script>
    async function copyToClipboard() {
        const copyText = document.getElementById("short-url").value;
        const copyButton = document.querySelector(".btn-outline-secondary");
        const originalHTML = copyButton.innerHTML;
        
        try {
            if (navigator.clipboard) {
                await navigator.clipboard.writeText(copyText);
            } else {
                const textarea = document.createElement('textarea');
                textarea.value = copyText;
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
            }
            
            copyButton.innerHTML = 'Copiado!';
            copyButton.classList.add('text-success');
            
            setTimeout(() => {
                copyButton.innerHTML = originalHTML;
                copyButton.classList.remove('text-success');
            }, 1500);
            
        } catch (err) {
            copyButton.innerHTML = 'Error';
            setTimeout(() => {
                copyButton.innerHTML = originalHTML;
            }, 1500);
        }
    }
    </script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# Rutas
@app.route('/')
def home():
    return redirect('/shorten')

@app.route('/shorten', methods=['GET', 'POST'])
def shorten_url():
    if request.method == 'POST':
        long_url = request.form.get('url')
        if not long_url:
            return "URL no proporcionada", 400
        
        hash_code = generate_unique_hash()
        short_url = f"{BASE_DOMAIN}/url/{hash_code}"
        save_url(hash_code, long_url)
        
        return render_template_string(HTML_TEMPLATE, short_url=short_url)
    
    return render_template_string(HTML_TEMPLATE)

@app.route('/url/<hash_code>')
def redirect_to_long_url(hash_code):
    urls = load_urls()
    long_url = urls.get(hash_code)
    if long_url:
        return redirect(long_url, code=302)
    return "URL no encontrada", 404

if __name__ == '__main__':
    app.run(debug=True)  # Ejecutar en HTTP para desarrollo