from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash
from database import db
from models import Usuario  # veremos models abaixo

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    usuario = Usuario.query.filter_by(username=data.get('username')).first()
    if not usuario or not check_password_hash(usuario.senha, data.get('senha', '')):
        return jsonify({'erro': 'Usuário ou senha inválidos'}), 401
    session['user_id'] = usuario.id
    return jsonify({
        'id': usuario.id,
        'nome': usuario.nome,
        'tipo': usuario.tipo,
        'username': usuario.username
    })