/* ============================================================
   SISTEMA ESCOLAR ES@Sistemas — app.js
   Arquivo central de utilidades do frontend
   ============================================================ */

// ─────────────────────────────────────────────
// CONFIGURAÇÃO GLOBAL
// ─────────────────────────────────────────────
const API_BASE = ''; // ex: 'http://localhost:5000' se frontend rodar separado
const APP_INFO = {
  nome: 'Sistema Escolar',
  marca: 'ES@SistemasEducacionais',
  ano: 2026,
  versao: '1.0.0'
};

// ─────────────────────────────────────────────
// UTILITÁRIOS GERAIS
// ─────────────────────────────────────────────
const App = {

  // ---------- SESSÃO / USUÁRIO ----------
  getUsuario() {
    try {
      return JSON.parse(localStorage.getItem('usuario') || '{}');
    } catch {
      return {};
    }
  },

  setUsuario(usuario) {
    localStorage.setItem('usuario', JSON.stringify(usuario));
  },

  logout() {
    localStorage.removeItem('usuario');
    document.cookie = 'usuario=; max-age=0; path=/';
    window.location.href = 'login.html';
  },

  exigirLogin() {
    const u = App.getUsuario();
    if (!u || !u.username) {
      window.location.href = 'login.html';
      return null;
    }
    return u;
  },

  exigirTipo(tipos) {
    const u = App.exigirLogin();
    if (!u) return null;
    const lista = Array.isArray(tipos) ? tipos : [tipos];
    if (!lista.includes(u.tipo)) {
      App.toast('Acesso negado para este perfil.', 'erro');
      setTimeout(() => window.location.href = 'dashboard.html', 1500);
      return null;
    }
    return u;
  },

  // ---------- CHAMADAS À API ----------
  async api(endpoint, options = {}) {
    const config = {
      method: options.method || 'GET',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {})
      }
    };

    if (options.body) {
      config.body = typeof options.body === 'string'
        ? options.body
        : JSON.stringify(options.body);
    }

    try {
      const resposta = await fetch(API_BASE + endpoint, config);

      // Se 401 → sessão expirada
      if (resposta.status === 401) {
        App.toast('Sessão expirada. Faça login novamente.', 'erro');
        setTimeout(() => App.logout(), 1200);
        throw new Error('Não autorizado');
      }

      const dados = await resposta.json().catch(() => ({}));

      if (!resposta.ok) {
        throw new Error(dados.mensagem || dados.erro || `Erro ${resposta.status}`);
      }
      return dados;
    } catch (erro) {
      if (!navigator.onLine) {
        App.toast('Sem conexão com a internet.', 'erro');
      } else if (!erro.message.includes('Não autorizado')) {
        console.error('[API]', erro);
      }
      throw erro;
    }
  },

  get(endpoint) { return App.api(endpoint); },
  post(endpoint, body) { return App.api(endpoint, { method: 'POST', body }); },
  put(endpoint, body) { return App.api(endpoint, { method: 'PUT', body }); },
  del(endpoint) { return App.api(endpoint, { method: 'DELETE' }); },

  // ---------- UPLOAD DE IMAGEM ----------
  async uploadImagem(arquivo) {
    if (!arquivo) throw new Error('Nenhum arquivo selecionado');

    // Validação
    if (!arquivo.type.startsWith('image/')) {
      throw new Error('O arquivo deve ser uma imagem');
    }
    if (arquivo.size > 2 * 1024 * 1024) {
      throw new Error('A imagem deve ter no máximo 2MB');
    }

    const formData = new FormData();
    formData.append('foto', arquivo);

    const resposta = await fetch(API_BASE + '/api/upload', {
      method: 'POST',
      credentials: 'include',
      body: formData
    });

    const dados = await resposta.json().catch(() => ({}));
    if (!resposta.ok) throw new Error(dados.mensagem || 'Falha no upload');
    return dados; // { sucesso: true, url: '...' }
  },

  // ---------- NOTIFICAÇÕES (TOAST) ----------
  toast(mensagem, tipo = 'info', duracao = 3500) {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    const icones = {
      sucesso: '✅',
      erro: '❌',
      info: 'ℹ️',
      aviso: '⚠️'
    };

    const toast = document.createElement('div');
    toast.className = `toast toast-${tipo}`;
    toast.innerHTML = `
      <span class="toast-icon">${icones[tipo] || 'ℹ️'}</span>
      <span class="toast-msg">${mensagem}</span>
      <button class="toast-close" aria-label="Fechar">×</button>
    `;

    toast.querySelector('.toast-close').onclick = () => toast.remove();
    container.appendChild(toast);

    setTimeout(() => {
      toast.classList.add('toast-sair');
      setTimeout(() => toast.remove(), 300);
    }, duracao);
  },

  // Atalhos
  sucesso(msg) { App.toast(msg, 'sucesso'); },
  erro(msg)    { App.toast(msg, 'erro'); },
  info(msg)    { App.toast(msg, 'info'); },
  aviso(msg)   { App.toast(msg, 'aviso'); },

  // ---------- FORMATAR DADOS ----------
  formatarData(iso, formato = 'br') {
    if (!iso) return '';
    const data = iso.includes('T') ? new Date(iso) : new Date(iso + 'T00:00:00');
    if (isNaN(data.getTime())) return iso;

    const dia = String(data.getDate()).padStart(2, '0');
    const mes = String(data.getMonth() + 1).padStart(2, '0');
    const ano = data.getFullYear();

    if (formato === 'br') return `${dia}/${mes}/${ano}`;
    if (formato === 'iso') return `${ano}-${mes}-${dia}`;
    return `${dia}/${mes}/${ano}`;
  },

  formatarHora(hora) {
    if (!hora) return '';
    return hora.slice(0, 5); // 'HH:MM'
  },

  formatarNota(valor) {
    if (valor === null || valor === undefined) return '—';
    return Number(valor).toFixed(1);
  },

  formatarPercentual(valor) {
    if (valor === null || valor === undefined) return '—';
    return `${Number(valor).toFixed(1)}%`;
  },

  // ---------- UTILITÁRIOS DOM ----------
  $(seletor) { return document.querySelector(seletor); },
  $$(seletor) { return Array.from(document.querySelectorAll(seletor)); },

  criarElemento(tag, props = {}, filhos = []) {
    const el = document.createElement(tag);
    Object.assign(el, props);
    const lista = Array.isArray(filhos) ? filhos : [filhos];
    lista.forEach(f => {
      if (typeof f === 'string') el.appendChild(document.createTextNode(f));
      else if (f instanceof Node) el.appendChild(f);
    });
    return el;
  },

  // ---------- SEGURANÇA (escapar HTML) ----------
  escapar(texto) {
    if (texto === null || texto === undefined) return '';
    return String(texto)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  },

  // ---------- MÁSCARAS ----------
  mascararTelefone(v) {
    return v.replace(/\D/g, '')
      .replace(/^(\d{2})(\d)/, '($1) $2')
      .replace(/(\d{5})(\d)/, '$1-$2')
      .replace(/(-\d{4})\d+?$/, '$1');
  },

  mascararData(v) {
    return v.replace(/\D/g, '')
      .replace(/(\d{2})(\d)/, '$1/$2')
      .replace(/(\d{2})(\d)/, '$1/$2')
      .replace(/(\/\d{4})\d+?$/, '$1');
  },

  // ---------- COOKIES ----------
  setCookie(nome, valor, dias = 7) {
    const expira = new Date();
    expira.setTime(expira.getTime() + dias * 24 * 60 * 60 * 1000);
    document.cookie = `${nome}=${encodeURIComponent(valor)}; expires=${expira.toUTCString()}; path=/; SameSite=Lax`;
  },

  getCookie(nome) {
    const cookies = document.cookie.split(';');
    for (const c of cookies) {
      const [k, v] = c.trim().split('=');
      if (k === nome) return decodeURIComponent(v || '');
    }
    return null;
  },

  // ---------- OFFLINE / CONEXÃO ----------
  monitorarConexao() {
    const aviso = () => {
      const banner = document.getElementById('offline-banner') || App._criarBannerOffline();
      banner.style.display = navigator.onLine ? 'none' : 'block';
    };
    window.addEventListener('online', () => {
      aviso();
      App.info('Conexão restabelecida!');
    });
    window.addEventListener('offline', () => {
      aviso();
      App.aviso('Você está offline. Algumas funções podem falhar.');
    });
    aviso();
  },

  _criarBannerOffline() {
    const b = document.createElement('div');
    b.id = 'offline-banner';
    b.style.cssText = `
      position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
      background: #E57373; color: white; text-align: center;
      padding: 8px; font-weight: 600; display: none;
    `;
    b.textContent = '⚠️ Você está offline — modo limitado';
    document.body.appendChild(b);
    return b;
  },

  // ---------- CONFIRMAÇÃO ----------
  async confirmar(mensagem) {
    return window.confirm(mensagem);
  },

  // ---------- DEBOUNCE ----------
  debounce(funcao, ms = 300) {
    let timer;
    return (...args) => {
      clearTimeout(timer);
      timer = setTimeout(() => funcao(...args), ms);
    };
  },

  // ---------- CRIAR BOTÃO LOADING ----------
  botaoLoading(botao, carregando = true) {
    if (carregando) {
      botao.dataset.textoOriginal = botao.textContent;
      botao.disabled = true;
      botao.textContent = 'Carregando...';
    } else {
      botao.textContent = botao.dataset.textoOriginal || 'Salvar';
      botao.disabled = false;
    }
  },

  // ---------- FORMATAR NOME ----------
  iniciais(nome) {
    if (!nome) return '?';
    const partes = nome.trim().split(/\s+/);
    if (partes.length === 1) return partes[0][0].toUpperCase();
    return (partes[0][0] + partes[partes.length - 1][0]).toUpperCase();
  },

  primeiroNome(nome) {
    if (!nome) return '';
    return nome.trim().split(/\s+/)[0];
  },

  // ---------- RENDERIZAR MENU CONFORME PERFIL ----------
    renderizarMenu(usuario) {
    const menus = {
      admin: [
        { nome: 'Início',       href: 'dashboard.html', icone: '🏠' },
        { nome: 'Alunos',       href: 'alunos.html',    icone: '👨‍🎓' },
        { nome: 'Professores',  href: 'professores.html', icone: '👩‍🏫' },
        { nome: 'Turmas',       href: 'turmas.html',    icone: '🏫' },
        { nome: 'Avisos',       href: 'mural.html',     icone: '📢' },
        { nome: 'Relatórios',   href: 'relatorios.html',icone: '📊' },
        { nome: 'Configurações',href: 'configuracoes.html', icone: '⚙️' },
        { nome: 'Perfil',       href: 'perfil.html',    icone: '👤' }
      ],
      professor: [
        { nome: 'Meu Painel',   href: 'painel-professor.html', icone: '🏠' },
        { nome: 'Lançar Frequência', href: 'frequencia.html', icone: '📋' },
        { nome: 'Lançar Notas', href: 'notas.html',     icone: '📝' },
        { nome: 'Mural',        href: 'mural.html',     icone: '📢' },
        { nome: 'Meu Perfil',   href: 'perfil.html',    icone: '👤' }
      ],
      aluno: [
        { nome: 'Meu Painel',   href: 'painel-aluno.html', icone: '🏠' },
        { nome: 'Minhas Notas', href: 'minhas-notas.html', icone: '📝' },
        { nome: 'Minha Frequência', href: 'minha-frequencia.html', icone: '📋' },
        { nome: 'Mural',        href: 'mural.html',     icone: '📢' },
        { nome: 'Meu Perfil',   href: 'perfil.html',    icone: '👤' }
      ]
    };

    const lista = menus[usuario.tipo] || [];
    const nav = document.getElementById('menu');
    if (!nav) return;

    const paginaAtual = window.location.pathname.split('/').pop() || (usuario.tipo === 'aluno' ? 'painel-aluno.html' : 'painel-professor.html');
    nav.innerHTML = '';

    lista.forEach(item => {
      const a = document.createElement('a');
      a.href = item.href;
      a.innerHTML = `<span class="menu-icone">${item.icone}</span> ${item.nome}`;
      if (item.href === paginaAtual) a.classList.add('active');
      nav.appendChild(a);
    });
  }
};

// ─────────────────────────────────────────────
// INICIALIZAÇÃO AUTOMÁTICA
// ─────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  App.monitorarConexao();

  // Banner de cookies (só se não aceitou)
  if (!localStorage.getItem('cookiesAceitos')) {
    const banner = document.getElementById('cookieBanner');
    if (banner) banner.style.display = 'flex';
  }
});

// ─────────────────────────────────────────────
// FUNÇÕES GLOBAIS PARA USO EM onclick=""
// ─────────────────────────────────────────────
window.aceitarCookies = function () {
  localStorage.setItem('cookiesAceitos', '1');
  App.setCookie('aceite_cookies', '1', 365);
  const banner = document.getElementById('cookieBanner');
  if (banner) banner.style.display = 'none';
  App.sucesso('Cookies aceitos. Obrigado!');
};

window.logout = function () {
  App.logout();
};

window.App = App;