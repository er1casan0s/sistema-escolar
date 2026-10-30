from flask import Blueprint, jsonify, request
from database import db
from models import Turma, Aluno

turmas_bp = Blueprint('turmas', __name__)

@turmas_bp.route('/', methods=['GET'])
def listar():
    turmas = Turma.query.order_by(Turma.ano, Turma.nome, Turma.turno).all()
    return jsonify([
        {
            'id': t.id, 
            'nome': t.nome, 
            'turno': t.turno, 
            'ano': t.ano,
            'qtd_alunos': Aluno.query.filter_by(turma_id=t.id, ex_aluno=False).count()
        } for t in turmas
    ])

@turmas_bp.route('/', methods=['POST'])
def criar():
    d = request.get_json()
    try:
        t = Turma(nome=d['nome'], turno=d['turno'], ano=d.get('ano', 2026))
        db.session.add(t)
        db.session.commit()
        return jsonify({'sucesso': True, 'mensagem': 'Turma criada com sucesso!', 'id': t.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'mensagem': f'Erro: {e}'}), 400

@turmas_bp.route('/<int:id>', methods=['PUT'])
def editar(id):
    t = Turma.query.get(id)
    if not t: return jsonify({'sucesso': False, 'mensagem': 'Turma não encontrada'}), 404
    d = request.get_json()
    try:
        if 'nome' in d: t.nome = d['nome']
        if 'turno' in d: t.turno = d['turno']
        if 'ano' in d: t.ano = d['ano']
        db.session.commit()
        return jsonify({'sucesso': True, 'mensagem': 'Turma atualizada!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'mensagem': f'Erro: {e}'}), 400

@turmas_bp.route('/<int:id>', methods=['DELETE'])
def excluir(id):
    t = Turma.query.get(id)
    if not t: return jsonify({'sucesso': False, 'mensagem': 'Turma não encontrada'}), 404
    
    # Verifica se tem alunos na turma antes de excluir
    if Aluno.query.filter_by(turma_id=id, ex_aluno=False).count() > 0:
        return jsonify({'sucesso': False, 'mensagem': 'Não é possível excluir: Há alunos cadastrados nesta turma.'}), 400

    try:
        db.session.delete(t)
        db.session.commit()
        return jsonify({'sucesso': True, 'mensagem': 'Turma excluída com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'mensagem': f'Erro: {e}'}), 400