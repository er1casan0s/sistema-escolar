from flask import Blueprint, jsonify, request
from database import db
from models import Frequencia, Aluno
from datetime import datetime

frequencia_bp = Blueprint('frequencia', __name__)

@frequencia_bp.route('/aluno/<int:aluno_id>', methods=['GET'])
def listar_aluno(aluno_id):
    registros = Frequencia.query.filter_by(aluno_id=aluno_id).all()
    total = len(registros)
    presencas = sum(1 for r in registros if r.presente)
    perc = (presencas / total * 100) if total > 0 else 100
    return jsonify({
        'total_aulas': total,
        'presencas': presencas,
        'faltas': total - presencas,
        'percentual': round(perc, 1),
        'status': 'ATENÇÃO' if perc < 75 else 'OK'
    })

@frequencia_bp.route('/turma/<int:turma_id>', methods=['GET'])
def listar_turma(turma_id):
    alunos = Aluno.query.filter_by(turma_id=turma_id, ex_aluno=False).all()
    resultado = []
    for a in alunos:
        registros = Frequencia.query.filter_by(aluno_id=a.id).all()
        total = len(registros)
        presencas = sum(1 for r in registros if r.presente)
        perc = (presencas / total * 100) if total > 0 else 100
        resultado.append({
            'aluno_id': a.id,
            'nome': a.usuario.nome,
            'percentual': round(perc, 1),
            'status': 'ATENÇÃO' if perc < 75 else 'OK'
        })
    return jsonify(resultado)

@frequencia_bp.route('/', methods=['POST'])
def registrar():
    d = request.get_json()
    try:
        data_aula = datetime.strptime(d['data'], '%Y-%m-%d').date()
        for item in d['presencas']:
            f = Frequencia(
                aluno_id=item['aluno_id'],
                turma_id=d['turma_id'],
                data=data_aula,
                presente=item['presente'],
                conteudo=d.get('conteudo', '')
            )
            db.session.add(f)
        db.session.commit()
        return jsonify({'sucesso': True, 'mensagem': 'Frequência registrada!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 400