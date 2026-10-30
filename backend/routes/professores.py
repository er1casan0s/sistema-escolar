from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash
from database import db
from models import Professor, Usuario, Disciplina, Turma

professores_bp = Blueprint('professores', __name__)


# ---------- LISTAR ----------
@professores_bp.route('/', methods=['GET'])
def listar():
    incluir_ex = request.args.get('ex', '0') == '1'
    query = Professor.query
    if not incluir_ex:
        query = query.filter_by(ex_professor=False)
    else:
        query = query.filter_by(ex_professor=True)

    professores = query.all()
    return jsonify([
        {
            'id': p.id,
            'usuario_id': p.usuario_id,
            'nome': p.usuario.nome,
            'username': p.usuario.username,
            'foto': p.usuario.foto,
            'disciplina': p.disciplina.nome if p.disciplina else None,
            'disciplina_id': p.disciplina_id,
            'dias_trabalho': p.dias_trabalho,
            'formacao': p.formacao,
            'turmas_ids': [t.id for t in p.turmas],
            'bio': p.bio,
            'ativo': p.usuario.ativo,
            'ex_professor': p.ex_professor
        }
        for p in professores
    ])


# ---------- BUSCAR UM ----------
@professores_bp.route('/<int:id>', methods=['GET'])
def buscar(id):
    p = Professor.query.get(id)
    if not p:
        return jsonify({'sucesso': False, 'mensagem': 'Professor não encontrado'}), 404

    return jsonify({
        'id': p.id,
        'usuario_id': p.usuario_id,
        'nome': p.usuario.nome,
        'username': p.usuario.username,
        'foto': p.usuario.foto,
        'disciplina': p.disciplina.nome if p.disciplina else None,
        'disciplina_id': p.disciplina_id,
        'dias_trabalho': p.dias_trabalho,
        'formacao': p.formacao,
        'bio': p.bio
    })


# ---------- CRIAR ----------
@professores_bp.route('/', methods=['POST'])
def criar():
    d = request.get_json() or {}
    try:
        if Usuario.query.filter_by(username=d.get('username')).first():
            return jsonify({'sucesso': False, 'mensagem': 'Nome de usuário já existe'}), 400

        u = Usuario(
            username=d['username'],
            senha=generate_password_hash(d.get('senha', 'teste123')),
            nome=d['nome'],
            tipo='professor',
            foto=d.get('foto', 'avatar-default.png')
        )
        db.session.add(u)
        db.session.flush()

        p = Professor(
            usuario_id=u.id,
            disciplina_id=d.get('disciplina_id'),
            dias_trabalho=d.get('dias_trabalho', ''),
            formacao=d.get('formacao', ''),
            bio=d.get('bio', '')
        )

        # --- COLE AQUI ---
        turmas_ids = d.get('turmas_ids', [])
        if turmas_ids:
            turmas = Turma.query.filter(Turma.id.in_(turmas_ids)).all()
            p.turmas = turmas
        # -----------------
        db.session.add(p)
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Professor cadastrado com sucesso!',
            'id': p.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'mensagem': f'Erro ao cadastrar: {e}'}), 400


# ---------- EDITAR ----------
@professores_bp.route('/<int:id>', methods=['PUT'])
def editar(id):
    p = Professor.query.get(id)
    if not p:
        return jsonify({'sucesso': False, 'mensagem': 'Professor não encontrado'}), 404

    d = request.get_json() or {}
    try:
        if 'nome' in d:
            p.usuario.nome = d['nome']
        if 'username' in d and d['username'] != p.usuario.username:
            if Usuario.query.filter_by(username=d['username']).first():
                return jsonify({'sucesso': False, 'mensagem': 'Username já em uso'}), 400
            p.usuario.username = d['username']
        if 'senha' in d and d['senha']:
            p.usuario.senha = generate_password_hash(d['senha'])
        if 'foto' in d:
            p.usuario.foto = d['foto']

        if 'disciplina_id' in d:
            p.disciplina_id = d['disciplina_id']
        if 'dias_trabalho' in d:
            p.dias_trabalho = d['dias_trabalho']
        if 'formacao' in d:
            p.formacao = d['formacao']
        if 'bio' in d:
            p.bio = d['bio']
        if 'turmas_ids' in d:
            turmas_ids = d['turmas_ids']
            turmas = Turma.query.filter(Turma.id.in_(turmas_ids)).all()
            p.turmas = turmas


        db.session.commit()
        return jsonify({'sucesso': True, 'mensagem': 'Professor atualizado com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'mensagem': f'Erro ao editar: {e}'}), 400


# ---------- EXCLUIR (move para banco de ex-professores) ----------
@professores_bp.route('/<int:id>', methods=['DELETE'])
def excluir(id):
    p = Professor.query.get(id)
    if not p:
        return jsonify({'sucesso': False, 'mensagem': 'Professor não encontrado'}), 404

    try:
        p.ex_professor = True
        p.usuario.ativo = False
        db.session.commit()
        return jsonify({'sucesso': True, 'mensagem': 'Professor movido para o banco de ex-professores'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'mensagem': f'Erro ao excluir: {e}'}), 400


# ---------- RESTAURAR EX-PROFESSOR ----------
@professores_bp.route('/<int:id>/restaurar', methods=['POST'])
def restaurar(id):
    p = Professor.query.get(id)
    if not p:
        return jsonify({'sucesso': False, 'mensagem': 'Professor não encontrado'}), 404

    try:
        p.ex_professor = False
        p.usuario.ativo = True
        db.session.commit()
        return jsonify({'sucesso': True, 'mensagem': 'Professor restaurado com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'mensagem': f'Erro ao restaurar: {e}'}), 400


# ---------- LISTAR DISCIPLINAS ----------
@professores_bp.route('/disciplinas', methods=['GET'])
def listar_disciplinas():
    # O .order_by(Disciplina.nome) coloca em ordem alfabética
    disciplinas = Disciplina.query.order_by(Disciplina.nome.asc()).all() 
    return jsonify([{'id': d.id, 'nome': d.nome} for d in disciplinas])


# ---------- CRIAR DISCIPLINA ----------
@professores_bp.route('/disciplinas', methods=['POST'])
def criar_disciplina():
    d = request.get_json() or {}
    nome = (d.get('nome') or '').strip()
    if not nome:
        return jsonify({'sucesso': False, 'mensagem': 'Nome da disciplina é obrigatório'}), 400

    if Disciplina.query.filter_by(nome=nome).first():
        return jsonify({'sucesso': False, 'mensagem': 'Disciplina já cadastrada'}), 400

    nova = Disciplina(nome=nome)
    db.session.add(nova)
    db.session.commit()
    return jsonify({'sucesso': True, 'mensagem': 'Disciplina cadastrada!', 'id': nova.id}), 201


# ---------- PERFIL PRÓPRIO (para professor logado) ----------
@professores_bp.route('/meu-perfil/<int:usuario_id>', methods=['GET'])
def meu_perfil(usuario_id):
    p = Professor.query.filter_by(usuario_id=usuario_id).first()
    if not p:
        return jsonify({'sucesso': False, 'mensagem': 'Perfil não encontrado'}), 404

    return jsonify({
        'nome': p.usuario.nome,
        'username': p.usuario.username,
        'foto': p.usuario.foto,
        'disciplina': p.disciplina.nome if p.disciplina else None,
        'dias_trabalho': p.dias_trabalho,
        'formacao': p.formacao,
        'bio': p.bio
    })


# ---------- ATUALIZAR PERFIL PRÓPRIO ----------
@professores_bp.route('/meu-perfil/<int:usuario_id>', methods=['PUT'])
def atualizar_meu_perfil(usuario_id):
    p = Professor.query.filter_by(usuario_id=usuario_id).first()
    if not p:
        return jsonify({'sucesso': False, 'mensagem': 'Perfil não encontrado'}), 404

    d = request.get_json() or {}
    try:
        if 'nome' in d: p.usuario.nome = d['nome']
        if 'foto' in d: p.usuario.foto = d['foto']
        if 'bio' in d: p.bio = d['bio']
        if 'formacao' in d: p.formacao = d['formacao']
        if 'dias_trabalho' in d: p.dias_trabalho = d['dias_trabalho']
        if 'senha' in d and d['senha']:
            p.usuario.senha = generate_password_hash(d['senha'])
        db.session.commit()
        return jsonify({'sucesso': True, 'mensagem': 'Perfil atualizado com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'mensagem': f'Erro: {e}'}), 400