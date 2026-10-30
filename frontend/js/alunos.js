document.addEventListener('DOMContentLoaded', () => {
  const usuario = App.exigirTipo('admin');
  if (!usuario) return;
  App.renderizarMenu(usuario);
  carregarTurmas();
});

function carregarTurmas() {
  const turmas = [
    { id: 1, nome: '1º Ano', turno: 'Manhã', cor: '#7CB9E8' },
    { id: 2, nome: '1º Ano', turno: 'Tarde', cor: '#A8D5BA' },
    { id: 3, nome: '2º Ano', turno: 'Manhã', cor: '#FFB74D' },
    { id: 4, nome: '2º Ano', turno: 'Tarde', cor: '#E57373' },
    { id: 5, nome: '3º Ano', turno: 'Manhã', cor: '#BA68C8' },
    { id: 6, nome: '3º Ano', turno: 'Tarde', cor: '#4DB6AC' }
  ];

  const grid = document.getElementById('grid-turmas');
  grid.innerHTML = turmas.map(t => `
    <div class="card-turma" style="border-top-color: ${t.cor}" onclick="abrirTurma(${t.id}, '${t.nome}', '${t.turno}')">
      <h3>${t.nome}</h3>
      <p>Turno: ${t.turno}</p>
      <span style="font-size: 13px; color: var(--azul-suave); font-weight: bold;">Ver alunos →</span>
    </div>
  `).join('');
}

function abrirTurma(id, nome, turno) {
  const painel = document.getElementById('painel-alunos');
  const titulo = document.getElementById('titulo-turma-selecionada');
  const tabela = document.getElementById('tabela-alunos');

  titulo.textContent = `Alunos do ${nome} (${turno})`;
  
  // Simulação de banco
  let alunos = [];
  if (id === 3) alunos = [{ nome: 'João Benício', turno: turno, freq: '80%' }];

  if (alunos.length === 0) {
    tabela.innerHTML = `<tr><td colspan="4" style="text-align:center;">Nenhum aluno cadastrado nesta turma ainda.</td></tr>`;
  } else {
    tabela.innerHTML = alunos.map(a => `
      <tr>
        <td>${a.nome}</td>
        <td>${a.turno}</td>
        <td><span class="badge sucesso">${a.freq}</span></td>
        <td><button class="btn-acao">Perfil</button></td>
      </tr>
    `).join('');
  }

  painel.classList.add('ativo');
  painel.scrollIntoView({ behavior: 'smooth' });
}

function fecharLista() {
  document.getElementById('painel-alunos').classList.remove('ativo');
}