from app import app
from database import db
from models import Usuario, Aluno, Professor, Turma, Disciplina, Configuracao
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()

    # Disciplinas
    info = Disciplina(nome='Informática')
    db.session.add(info); db.session.flush()

    # Turmas
    nomes = ['1 Ano', '2 Ano', '3 Ano']
    turmas = {}
    for n in nomes:
        for t in ['manhã', 'tarde']:
            t_ = Turma(nome=n, turno=t, ano=2026)
            db.session.add(t_); db.session.flush()
            turmas[f'{n}-{t}'] = t_.id

    # ADMIN - maria
    u_admin = Usuario(username='maria', nome='Maria (Coordenação)',
                      senha=generate_password_hash('teste123'),
                      tipo='admin', foto='avatar-default.png')
    db.session.add(u_admin)

    # PROFESSOR - ericasantos
    u_prof = Usuario(username='ericasantos', nome='Erica Santos',
                     senha=generate_password_hash('teste123'),
                     tipo='professor', foto='avatar-default.png')
    db.session.add(u_prof); db.session.flush()
    p = Professor(usuario_id=u_prof.id, disciplina_id=info.id,
                  dias_trabalho='Seg, Ter, Qua, Qui, Sex',
                  formacao='Licenciatura em Informática',
                  bio='Professora de Informática das turmas de 1º, 2º e 3º ano.')
    db.session.add(p)

    # ALUNO - joaobenicio
    u_aluno = Usuario(username='joaobenicio', nome='João Benício',
                      senha=generate_password_hash('teste123'),
                      tipo='aluno', foto='avatar-default.png')
    db.session.add(u_aluno); db.session.flush()
    a = Aluno(usuario_id=u_aluno.id, turma_id=turmas['2 Ano-manhã'],
              turno='manhã', bio='Aluno do 2º ano, adora tecnologia.')
    db.session.add(a)

    # Configurações da escola
    for k, v in [
        ('nome_escola', 'Escola Exemplo ES@'),
        ('metodo_avaliacao', 'bimestral'),
        ('media_minima', '6')
    ]:
        db.session.add(Configuracao(chave=k, valor=v))

    db.session.commit()
    print('✅ Banco populado com sucesso')