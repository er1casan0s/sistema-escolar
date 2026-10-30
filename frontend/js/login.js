document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('form-login');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value.trim();
    const senha = document.getElementById('senha').value;
    const botao = form.querySelector('button[type="submit"]');

    try {
      App.botaoLoading(botao, true);
      // Faz o login
      const dados = await App.post('/api/auth/login', { username, senha });
      App.setUsuario(dados);
      App.setCookie('usuario', dados.username, 7);
      
      App.sucesso('Bem-vindo(a), ' + App.primeiroNome(dados.nome) + '!');

      // Redireciona baseado no tipo de usuário
      setTimeout(() => {
        if (dados.tipo === 'admin') {
          window.location.href = 'dashboard.html'; // Painel Admin
        } else if (dados.tipo === 'professor') {
          window.location.href = 'painel-professor.html';
        } else if (dados.tipo === 'aluno') {
          window.location.href = 'painel-aluno.html';
        }
      }, 800);
      
    } catch (erro) {
      App.erro(erro.message || 'Não foi possível entrar');
    } finally {
      App.botaoLoading(botao, false);
    }
  });
});