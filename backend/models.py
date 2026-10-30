from database import db
from datetime import datetime


professor_turma = db.Table('professor_turma',
    db.Column('professor_id', db.Integer, db.ForeignKey('professores.id'), primary_key=True),
    db.Column('turma_id', db.Integer, db.ForeignKey('turmas.id'), primary_key=True)
)

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    nome = db.Column(db.String(120), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # aluno, professor, admin
    foto = db.Column(db.String(255), default='avatar-default.png')
    ativo = db.Column(db.Boolean, default=True)

class Aluno(db.Model):
    __tablename__ = 'alunos'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    turma_id = db.Column(db.Integer, db.ForeignKey('turmas.id'))
    turno = db.Column(db.String(20))
    observacoes = db.Column(db.Text)
    atipicidades = db.Column(db.String(255))  # TEA, TDAH, etc
    obs_medicas = db.Column(db.Text)
    bio = db.Column(db.Text)
    ex_aluno = db.Column(db.Boolean, default=False)
    usuario = db.relationship('Usuario')
    turma = db.relationship('Turma')

class Professor(db.Model):
    __tablename__ = 'professores'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    disciplina_id = db.Column(db.Integer, db.ForeignKey('disciplinas.id'))
    dias_trabalho = db.Column(db.String(200))
    formacao = db.Column(db.Text)
    bio = db.Column(db.Text)
    ex_professor = db.Column(db.Boolean, default=False)
    usuario = db.relationship('Usuario')
    disciplina = db.relationship('Disciplina')
    turmas = db.relationship('Turma', secondary=professor_turma, backref='professores')

class Disciplina(db.Model):
    __tablename__ = 'disciplinas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True, nullable=False)

class Turma(db.Model):
    __tablename__ = 'turmas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)      # "1 Ano"
    turno = db.Column(db.String(20), nullable=False)     # manhã/tarde
    ano = db.Column(db.Integer, default=2026)

class Frequencia(db.Model):
    __tablename__ = 'frequencias'
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'))
    turma_id = db.Column(db.Integer, db.ForeignKey('turmas.id'))
    data = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.String(10))
    hora_fim = db.Column(db.String(10))
    presente = db.Column(db.Boolean, default=True)
    conteudo = db.Column(db.Text)  # o que foi feito

class Nota(db.Model):
    __tablename__ = 'notas'
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'))
    disciplina_id = db.Column(db.Integer, db.ForeignKey('disciplinas.id'))
    bimestre = db.Column(db.Integer)   # 1..4
    valor = db.Column(db.Float)

class Aviso(db.Model):
    __tablename__ = 'avisos'
    id = db.Column(db.Integer, primary_key=True)
    autor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    titulo = db.Column(db.String(150))
    mensagem = db.Column(db.Text)
    destinatario_tipo = db.Column(db.String(20))  # turma, aluno, professor
    destinatario_id = db.Column(db.Integer)
    data = db.Column(db.DateTime, default=datetime.utcnow)

class Configuracao(db.Model):
    __tablename__ = 'configuracoes'
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(50), unique=True)
    valor = db.Column(db.String(255))