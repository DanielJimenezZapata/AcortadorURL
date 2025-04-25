from flask import Flask, redirect, request, render_template_string
import hashlib

app = Flask(__name__)

# Base de datos simulada
url_database = {}

# HTML + CSS + Bootstrap (interfaz moderna)
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
            Versión 1.0
        </div>
    </div>

    <script>
    async function copyToClipboard() {
        const copyText = document.getElementById("short-url").value;
        const copyButton = document.querySelector(".btn-outline-secondary");
        const originalHTML = copyButton.innerHTML;
        
        try {
            // Intentar con la API moderna primero
            if (navigator.clipboard) {
                await navigator.clipboard.writeText(copyText);
            } else {
                // Fallback para navegadores antiguos
                const textarea = document.createElement('textarea');
                textarea.value = copyText;
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
            }
            
            // Feedback visual elegante
            copyButton.innerHTML = '<i class="bi bi-check2"></i> Copiado';
            copyButton.classList.add('text-success');
            
            // Restaurar después de 1.5 segundos
            setTimeout(() => {
                copyButton.innerHTML = originalHTML;
                copyButton.classList.remove('text-success');
            }, 1500);
            
        } catch (err) {
            copyButton.innerHTML = '<i class="bi bi-x"></i> Error';
            console.error("Error al copiar: ", err);
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

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/shorten', methods=['POST'])
def shorten_url():
    long_url = request.form.get('url')
    if not long_url:
        return "URL no proporcionada", 400
    
    # Genera un hash único
    hash_code = hashlib.md5(long_url.encode()).hexdigest()[:8]
    short_url = f"http://localhost:5000/{hash_code}"  
    
    # Guarda en la base de datos con la parte final del hash
    url_database[hash_code] = long_url
    
    return render_template_string(HTML_TEMPLATE, short_url=short_url)

@app.route('/<hash_code>')
def redirect_to_long_url(hash_code):
    long_url = url_database.get(hash_code)
    if long_url:
        return redirect(long_url, code=302)
    return "URL no encontrada", 404

if __name__ == '__main__':
    app.run(debug=True)