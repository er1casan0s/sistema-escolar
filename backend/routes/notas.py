from flask import Blueprint, jsonify, request
from database import db
from models import Nota, Aluno, Turma, Disciplina, Configuracao

notas_bp = Blueprint('notas', __name__)


# ---------- Utilitário: pegar configuração da escola ----------
def get_config(chave, default=None):
    c = Configuracao.query.filter_by(chave=chave).first()
    return c.valor if c else default


def calcular_media_final(valores, metodo):
    """Calcula média final conforme o método configurado."""
    valores = [v for v in valores if v is not None]
    if not valores:
        return None
    if metodo == 'bimestral':   # 4 notas
        soma = sum(valores[:4])
        return round(soma / 4, 2) if len(valores) >= 4 else round(sum(valores)/len(valores), 2)
    if metodo == 'trimestre':   # 3 notas
        soma = sum(valores[:3])
        return round(soma / 3, 2) if len(valores) >= 3 else round(sum(valores)/len(valores), 2)
    if metodo == 'semestre':    # 2 notas
        soma = sum(valores[:2])
        return round(soma / 2, 2) if len(valores) >= 2 else round(sum(valores)/len(valores), 2)
    return None


# ---------- LANÇAR / ATUALIZAR NOTA ----------
@notas_bp.route('/', methods=['POST'])
def lancar():
    d = request.get_json() or {}
    try:
        aluno_id = d.get('aluno_id')
        disciplina_id = d.get('disciplina_id')
        bimestre = d.get('bimestre')
        valor = d.get('valor')

        if not all([aluno_id, disciplina_id, bimestre is not None, valor is not None]):
            return jsonify({'sucesso': False, 'mensagem': 'Dados incompletos'}), 400

        if not Aluno.query.get(aluno_id):
            return jsonify({'sucesso': False, 'mensagem': 'Aluno não encontrado'}), 404
        if not Disciplina.query.get(disciplina_id):
            return jsonify({'sucesso': False, 'mensagem': 'Disciplina não encontrada'}), 404

        # Atualiza se já existir; senão cria
        nota = Nota.query.filter_by(
            aluno_id=aluno_id, disciplina_id=disciplina_id, bimestre=bimestre
        ).first()

        if nota:
            nota.valor = float(valor)
            msg = 'Nota atualizada com sucesso!'
        else:
            nota = Nota(
                aluno_id=aluno_id,
                disciplina_id=disciplina_id,
                bimestre=bimestre,
                valor=float(valor)
            )
            db.session.add(nota)
            msg = 'Nota lançada com sucesso!'

        db.session.commit()
        return jsonify({'sucesso': True, 'mensagem': msg, 'id': nota.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'mensagem': f'Erro ao lançar nota: {e}'}), 400


# ---------- LANÇAR VÁRIAS NOTAS DE UMA VEZ ----------
@notas_bp.route('/lote', methods=['POST'])
def lancar_lote():
    d = request.get_json() or {}
    disciplina_id = d.get('disciplina_id')
    bimestre = d.get('bimestre')
    notas = d.get('notas', [])  # [{aluno_id, valor}, ...]

    if not disciplina_id or bimestre is None:
        return jsonify({'sucesso': False, 'mensagem': 'Disciplina e bimestre são obrigatórios'}), 400

    try:
        lancadas = 0
        for item in notas:
            if item.get('valor') is None or item.get('valor') == '':
                continue
            nota = Nota.query.filter_by(
                aluno_id=item['aluno_id'],
                disciplina_id=disciplina_id,
                bimestre=bimestre
            ).first()
            if nota:
                nota.valor = float(item['valor'])
            else:
                db.session.add(Nota(
                    aluno_id=item['aluno_id'],
                    disciplina_id=disciplina_id,
                    bimestre=bimestre,
                    valor=float(item['valor'])
                ))
            lancadas += 1

        db.session.commit()
        return jsonify({
            'sucesso': True,
            'mensagem': f'{lancadas} nota(s) salva(s) com sucesso!'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'mensagem': f'Erro no lote: {e}'}), 400


# ---------- LISTAR NOTAS DE UM ALUNO ----------
@notas_bp.route('/aluno/<int:aluno_id>', methods=['GET'])
def notas_do_aluno(aluno_id):
    aluno = Aluno.query.get(aluno_id)
    if not aluno:
        return jsonify({'sucesso': False, 'mensagem': 'Aluno não encontrado'}), 404

    metodo = get_config('metodo_avaliacao', 'bimestral')
    media_minima = float(get_config('media_minima', '6'))

    notas = Nota.query.filter_by(aluno_id=aluno_id).all()

    # Agrupa por disciplina
    por_disciplina = {}
    for n in notas:
        disc = Disciplina.query.get(n.disciplina_id)
        key = disc.nome if disc else f'Disciplina {n.disciplina_id}'
        por_disciplina.setdefault(key, {'disciplina_id': n.disciplina_id, 'valores': {}})
        por_disciplina[key]['valores'][n.bimestre] = n.valor

    resultado = []
    aprovado_geral = True

    for disc_nome, info in por_disciplina.items():
        valores_ordenados = [info['valores'].get(i) for i in sorted(info['valores'].keys())]
        media = calcular_media_final(valores_ordenados, metodo)
        status = 'APROVADO'
        if media is not None and media < media_minima:
            status = 'RECUPERAÇÃO'
            aprovado_geral = False

        resultado.append({
            'disciplina': disc_nome,
            'disciplina_id': info['disciplina_id'],
            'notas': info['valores'],
            'media_final': media,
            'status': status
        })

    return jsonify({
        'aluno': {
            'id': aluno.id,
            'nome': aluno.usuario.nome,
            'turma': aluno.turma.nome if aluno.turma else None,
            'turno': aluno.turno
        },
        'metodo_avaliacao': metodo,
        'media_minima': media_minima,
        'disciplinas': resultado,
        'situacao_geral': 'APROVADO' if aprovado_geral else 'ATENÇÃO'
    })


# ---------- LISTAR NOTAS DE UMA TURMA + DISCIPLINA ----------
@notas_bp.route('/turma/<int:turma_id>/disciplina/<int:disciplina_id>', methods=['GET'])
def notas_turma_disciplina(turma_id, disciplina_id):
    turma = Turma.query.get(turma_id)
    if not turma:
        return jsonify({'sucesso': False, 'mensagem': 'Turma não encontrada'}), 404

    disciplina = Disciplina.query.get(disciplina_id)
    if not disciplina:
        return jsonify({'sucesso': False, 'mensagem': 'Disciplina não encontrada'}), 404

    alunos = Aluno.query.filter_by(turma_id=turma_id, ex_aluno=False).all()
    metodo = get_config('metodo_avaliacao', 'bimestral')

    resultado = []
    for a in alunos:
        notas = Nota.query.filter_by(aluno_id=a.id, disciplina_id=disciplina_id).all()
        valores = {n.bimestre: n.valor for n in notas}
        lista = [valores.get(i) for i in sorted(valores.keys())]
        media = calcular_media_final(lista, metodo)
        resultado.append({
            'aluno_id': a.id,
            'nome': a.usuario.nome,
            'notas': valores,
            'media_final': media
        })

    return jsonify({
        'turma': {'id': turma.id, 'nome': turma.nome, 'turno': turma.turno},
        'disciplina': {'id': disciplina.id, 'nome': disciplina.nome},
        'metodo_avaliacao': metodo,
        'alunos': resultado
    })


# ---------- EXCLUIR NOTA ----------
@notas_bp.route('/<int:id>', methods=['DELETE'])
def excluir(id):
    nota = Nota.query.get(id)
    if not nota:
        return jsonify({'sucesso': False, 'mensagem': 'Nota não encontrada'}), 404
    try:
        db.session.delete(nota)
        db.session.commit()
        return jsonify({'sucesso': True, 'mensagem': 'Nota excluída com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'mensagem': f'Erro: {e}'}), 400


# ---------- RELATÓRIO (boletim) — apenas coordenação ----------
@notas_bp.route('/boletim/<int:aluno_id>', methods=['GET'])
def boletim(aluno_id):
    aluno = Aluno.query.get(aluno_id)
    if not aluno:
        return jsonify({'sucesso': False, 'mensagem': 'Aluno não encontrado'}), 404

    metodo = get_config('metodo_avaliacao', 'bimestral')
    media_minima = float(get_config('media_minima', '6'))
    nome_escola = get_config('nome_escola', 'Escola ES@')

    notas = Nota.query.filter_by(aluno_id=aluno_id).all()
    disciplinas = Disciplina.query.all()

    boletim = []
    for disc in disciplinas:
        valores = {n.bimestre: n.valor for n in notas if n.disciplina_id == disc.id}
        if not valores:
            continue
        lista = [valores.get(i) for i in sorted(valores.keys())]
        media = calcular_media_final(lista, metodo)
        boletim.append({
            'disciplina': disc.nome,
            'notas': valores,
            'media': media,
            'situacao': 'Aprovado' if (media or 0) >= media_minima else 'Recuperação'
        })

    return jsonify({
        'escola': nome_escola,
        'aluno': {
            'nome': aluno.usuario.nome,
            'turma': aluno.turma.nome if aluno.turma else None,
            'turno': aluno.turno
        },
        'metodo_avaliacao': metodo,
        'media_minima': media_minima,
        'boletim': boletim
    })

# Cole isso no final do arquivo notas.py
@notas_bp.route('/media-global/<int:aluno_id>', methods=['GET'])
def media_global(aluno_id):
    from models import Nota, Disciplina
    from routes.notas import calcular_media_final, get_config
    metodo = get_config('metodo_avaliacao', 'bimestral')
    
    notas = Nota.query.filter_by(aluno_id=aluno_id).all()
    disciplinas = Disciplina.query.all()
    
    medias = []
    for disc in disciplinas:
        valores = [n.valor for n in notas if n.disciplina_id == disc.id]
        if valores:
            media = calcular_media_final(valores, metodo)
            if media is not None:
                medias.append(media)
                
    if not medias:
        return jsonify({'media_global': 0.0})
        
    return jsonify({'media_global': round(sum(medias) / len(medias), 2)})