# backend/routes/__init__.py
# Torna a pasta "routes" um pacote Python.
# Os blueprints são importados diretamente no app.py.



from routes.alunos import alunos_bp
from routes.professores import professores_bp
from routes.turmas import turmas_bp
from routes.notas import notas_bp
from routes.frequencia import frequencia_bp
from routes.mural import mural_bp
from routes.admin import admin_bp