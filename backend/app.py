import os
from pathlib import Path
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from database import db, init_db

# Importação dos blueprints
from routes.alunos import alunos_bp
from routes.professores import professores_bp
from routes.turmas import turmas_bp
from routes.notas import notas_bp
from routes.frequencia import frequencia_bp
from routes.mural import mural_bp
from routes.admin import admin_bp
from auth import auth_bp

# =========================================================
# CONFIGURAÇÃO DE CAMINHOS ABSOLUTOS E SEGUROS
# =========================================================
# Descobre a pasta onde o app.py está (backend)
BASE_DIR = Path(__file__).resolve().parent
# Descobre a pasta raiz do projeto (sistema-escolar)
ROOT_DIR = BASE_DIR.parent
# Define as pastas frontend e database corretamente
FRONTEND_DIR = ROOT_DIR / 'frontend'
DATABASE_DIR = ROOT_DIR / 'database'
DB_PATH = DATABASE_DIR / 'escola.db'

# Cria as pastas se não existirem
os.makedirs(DATABASE_DIR, exist_ok=True)
os.makedirs(BASE_DIR / 'uploads', exist_ok=True)

# =========================================================
# INICIALIZAÇÃO DO APP
# =========================================================
app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path='')
CORS(app)

app.config['SECRET_KEY'] = 'troque-esta-chave-em-producao-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = str(BASE_DIR / 'uploads')

init_db(app)

# Registro dos blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(alunos_bp, url_prefix='/api/alunos')
app.register_blueprint(professores_bp, url_prefix='/api/professores')
app.register_blueprint(turmas_bp, url_prefix='/api/turmas')
app.register_blueprint(notas_bp, url_prefix='/api/notas')
app.register_blueprint(frequencia_bp, url_prefix='/api/frequencia')
app.register_blueprint(mural_bp, url_prefix='/api/mural')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

# =========================================================
# ROTAS DE ARQUIVOS ESTÁTICOS (A MÁGICA ACONTECE AQUI)
# =========================================================
@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

# Rota coringa para capturar qualquer .html e arquivos estáticos
@app.route('/<path:path>')
def serve_static(path):
    # Se o arquivo existir na pasta frontend, ele entrega
    if (FRONTEND_DIR / path).exists():
        return send_from_directory(FRONTEND_DIR, path)
    # Se for um upload, entrega da pasta uploads
    if path.startswith('uploads/'):
        return send_from_directory(app.config['UPLOAD_FOLDER'], path.replace('uploads/', ''))
    
    return jsonify({"erro": "Arquivo não encontrado no servidor"}), 404

# =========================================================
# START
# =========================================================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)