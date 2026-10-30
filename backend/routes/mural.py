from flask import Blueprint, jsonify, request
from database import db
from models import Aviso, Usuario, Aluno, Professor

mural_bp = Blueprint('mural', __name__)

@mural_bp.route('/', methods=['GET'])
def listar():
    avisos = Aviso.query.order_by(Aviso.data.desc()).all()
    resultado = []
    for a in avisos:
        autor = Usuario.query.get(a.autor_id)
        resultado.append({
            'id': a.id,
            'autor_nome': autor.nome if autor else 'Desconhecido',
            'titulo': a.titulo,
            'mensagem': a.mensagem,
            'data': a.data.strftime('%d/%m/%Y %H:%M'),
            'destinatario_tipo': a.destinatario_tipo
        })
    return jsonify(resultado)

@mural_bp.route('/', methods=['POST'])
def postar():
    d = request.get_json()
    try:
        a = Aviso(
            autor_id=d['autor_id'],
            titulo=d.get('titulo', 'Sem título'),
            mensagem=d['mensagem'],
            destinatario_tipo=d.get('destinatario_tipo', 'geral'),
            destinatario_id=d.get('destinatario_id')
        )
        db.session.add(a)
        db.session.commit()
        return jsonify({'sucesso': True, 'mensagem': 'Aviso publicado!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 400