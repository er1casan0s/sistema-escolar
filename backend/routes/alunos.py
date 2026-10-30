from flask import Blueprint, jsonify, request
from database import db
from models import Aluno, Usuario, Turma
from werkzeug.security import generate_password_hash

alunos_bp = Blueprint('alunos', __name__)

# ==========================================
# 1. LISTAR ALUNOS
# ==========================================
@alunos_bp.route('/', methods=['GET'])
def listar():
    turma_id = request.args.get('turma_id')
    query = Aluno.query.filter_by(ex_aluno=False)
    
    if turma_id:
        query = query.filter_by(turma_id=turma_id)
        
    alunos = query.all()
    return jsonify([
        {
            'id': a.id,
            'nome': a.usuario.nome,
            'username': a.usuario.username,
            'turma': a.turma.nome if a.turma else None,
            'turno': a.turno,
            'atipicidades': a.atipicidades
        } for a in alunos
    ])

# ==========================================
# 2. CRIAR (CADASTRAR) NOVO ALUNO
# ==========================================
@alunos_bp.route('/', methods=['POST'])
def criar():
    d = request.get_json()
    try:
        if Usuario.query.filter_by(username=d['username']).first():
            return jsonify({'sucesso': False, 'mensagem': 'Nome de usuário já existe'}), 400

        u = Usuario(
            username=d['username'],
            senha=generate_password_hash(d.get('senha', 'teste123')),
            nome=d['nome'],
            tipo='aluno'
        )
        db.session.add(u)
        db.session.flush() # Pega o ID do usuário criado

        # Descobre o turno da turma
        turma = Turma.query.get(d.get('turma_id'))
        turno = turma.turno if turma else ''

        a = Aluno(
            usuario_id=u.id,
            turma_id=d.get('turma_id'),
            turno=turno,
            atipicidades=d.get('atipicidades'),
            observacoes=d.get('observacoes'),
        )
        db.session.add(a)
        db.session.commit()
        return jsonify({'sucesso': True, 'mensagem': 'Aluno cadastrado com sucesso!', 'id': a.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'mensagem': f'Erro ao cadastrar: {e}'}), 400

# ==========================================
# 3. BUSCAR UM ALUNO ESPECÍFICO (Para o Editar)
# ==========================================
@alunos_bp.route('/<int:id>', methods=['GET'])
def buscar_aluno(id):
    a = Aluno.query.get(id)
    if not a:
        return jsonify({'sucesso': False, 'mensagem': 'Aluno não encontrado'}), 404
    
    return jsonify({
        'id': a.id,
        'nome': a.usuario.nome,
        'username': a.usuario.username,
        'turma_id': a.turma_id,
        'turno': a.turno,
        'atipicidades': a.atipicidades,
        'observacoes': a.observacoes
    })

# ==========================================
# 4. EDITAR O ALUNO
# ==========================================
@alunos_bp.route('/<int:id>', methods=['PUT'])
def editar_aluno(id):
    a = Aluno.query.get(id)
    if not a:
        return jsonify({'sucesso': False, 'mensagem': 'Aluno não encontrado'}), 404
        
    d = request.get_json()
    try:
        if 'nome' in d:
            a.usuario.nome = d['nome']

        # Verifica se o usuário está tentando mudar o username e se ele já existe
        if 'username' in d and d['username'] != a.usuario.username:
            if Usuario.query.filter_by(username=d['username']).first():
                return jsonify({'sucesso': False, 'mensagem': 'Este nome de usuário já está em uso'}), 400
            a.usuario.username = d['username']

        # Atualiza a senha se uma nova for enviada
        if 'senha' in d and d['senha']:
            a.usuario.senha = generate_password_hash(d['senha'])
            
        if 'turma_id' in d:
            a.turma_id = d['turma_id']
            turma = Turma.query.get(d['turma_id'])
            if turma:
                a.turno = turma.turno
                
        if 'atipicidades' in d:
            a.atipicidades = d['atipicidades']
            
        db.session.commit()
        return jsonify({'sucesso': True, 'mensagem': 'Aluno atualizado com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'mensagem': f'Erro: {e}'}), 400

# ==========================================
# 5. EXCLUIR ALUNO (Manda para ex-alunos)
# ==========================================
@alunos_bp.route('/<int:id>', methods=['DELETE'])
def excluir(id):
    a = Aluno.query.get(id)
    if not a: return jsonify({'sucesso': False, 'mensagem': 'Aluno não encontrado'}), 404
    try:
        a.ex_aluno = True   
        a.usuario.ativo = False
        db.session.commit()
        return jsonify({'sucesso': True, 'mensagem': 'Aluno movido para ex-alunos'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'mensagem': f'Erro: {e}'}), 400