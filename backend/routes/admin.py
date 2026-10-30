from flask import Blueprint, jsonify, request, send_file
from database import db
from models import Configuracao, Aluno, Professor, Turma, Nota, Frequencia
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from openpyxl import Workbook

admin_bp = Blueprint('admin', __name__)

# ================================================================
# CONFIGURAÇÕES DA ESCOLA
# ================================================================
@admin_bp.route('/configuracoes', methods=['GET'])
def get_configuracoes():
    configs = Configuracao.query.all()
    dados = {c.chave: c.valor for c in configs}
    # Define padrões caso o banco esteja vazio
    dados.setdefault('nome_escola', 'Escola ES@')
    dados.setdefault('logo_escola', '')
    dados.setdefault('metodo_avaliacao', 'bimestral')
    dados.setdefault('media_minima', '6')
    return jsonify(dados)

@admin_bp.route('/configuracoes', methods=['PUT'])
def atualizar_configuracoes():
    d = request.get_json()
    try:
        for chave, valor in d.items():
            c = Configuracao.query.filter_by(chave=chave).first()
            if c:
                c.valor = str(valor)
            else:
                db.session.add(Configuracao(chave=chave, valor=str(valor)))
        db.session.commit()
        return jsonify({'sucesso': True, 'mensagem': 'Configurações salvas!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 400

# ================================================================
# ESTATÍSTICAS GERAIS
# ================================================================
@admin_bp.route('/estatisticas', methods=['GET'])
def estatisticas():
    total_alunos = Aluno.query.filter_by(ex_aluno=False).count()
    total_professores = Professor.query.filter_by(ex_professor=False).count()
    total_turmas = Turma.query.count()
    return jsonify({
        'total_alunos': total_alunos,
        'total_professores': total_professores,
        'total_turmas': total_turmas
    })

# ================================================================
# RELATÓRIOS (PDF E EXCEL)
# ================================================================
@admin_bp.route('/relatorio/lista-presenca/<int:turma_id>', methods=['GET'])
def gerar_pdf_presenca(turma_id):
    turma = Turma.query.get(turma_id)
    if not turma:
        return jsonify({"erro": "Turma não encontrada"}), 404
        
    alunos = Aluno.query.filter_by(turma_id=turma_id, ex_aluno=False).all()
    escola = Configuracao.query.filter_by(chave='nome_escola').first()
    nome_escola = escola.valor if escola else 'Escola ES@'

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    # Cabeçalho do PDF
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, f"{nome_escola} - Lista de Presença")
    p.setFont("Helvetica", 12)
    p.drawString(100, 780, f"Turma: {turma.nome} ({turma.turno}) | Data: ____/____/______")
    
    # Linhas da tabela
    y = 730
    p.setFont("Helvetica", 10)
    p.drawString(50, y, "Nome do Aluno")
    p.drawString(400, y, "Assinatura")
    p.line(50, y-5, 550, y-5)
    y -= 30

    for aluno in alunos:
        p.drawString(50, y, aluno.usuario.nome)
        p.line(400, y-5, 550, y-5)
        y -= 25
        if y < 50: # Nova página se acabar o espaço
            p.showPage()
            y = 800

    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f'lista_presenca_{turma.nome}.pdf', mimetype='application/pdf')

@admin_bp.route('/relatorio/excel-notas/<int:turma_id>', methods=['GET'])
def gerar_excel_notas(turma_id):
    turma = Turma.query.get(turma_id)
    if not turma:
        return jsonify({"erro": "Turma não encontrada"}), 404
        
    alunos = Aluno.query.filter_by(turma_id=turma_id, ex_aluno=False).all()
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Notas"
    ws.append(["Nome", "Turma", "Nota 1", "Nota 2", "Nota 3", "Nota 4", "Média"])
    
    for a in alunos:
        ws.append([a.usuario.nome, turma.nome, "", "", "", "", ""])
        
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f'notas_{turma.nome}.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')