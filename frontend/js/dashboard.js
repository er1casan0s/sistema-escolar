document.addEventListener('DOMContentLoaded', () => {
  const usuario = App.exigirLogin();
  if (!usuario) return;

  App.renderizarMenu(usuario);
  
  const conteudo = document.getElementById('conteudo');
  if (!conteudo) return;

  const primeiroNome = usuario.nome.split(' ')[0];

  conteudo.innerHTML = `
    <div class="header-pagina">
      <h2>Olá, ${primeiroNome}! 👋</h2>
      <button onclick="logout()" class="btn-acao" style="border-color: #E57373; color: #E57373;">Sair do Sistema</button>
    </div>

    <div class="card">
      <h3>Bem-vindo(a) ao Sistema Escolar ES@</h3>
      <p>Você está logado como: <strong>${usuario.tipo.toUpperCase()}</strong></p>
      <p>Seu nome de usuário: @${usuario.username}</p>
    </div>

    <div class="card">
      <h3>Atalhos Rápidos</h3>
      <p>Use o menu lateral esquerdo para navegar pelas telas do sistema.</p>
    </div>
  `;
});