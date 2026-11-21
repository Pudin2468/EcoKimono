// EcoKimono - comportamentos da página (só o que o HTML não faz sozinho)

// 1) Filtro da lista de kimonos -------------------------------------------
const filtros = document.querySelector(".filtros");
if (filtros) {
  const botoes = filtros.querySelectorAll("[data-filtro]");        // os botões de filtro
  const linhas = document.querySelectorAll(".etiquetas [data-status]"); // cada kimono da lista
  const semResultado = document.getElementById("sem-resultado");   // aviso de lista vazia

  function aplicar(situacao) {
    let visiveis = 0;
    linhas.forEach((linha) => {
      // esconde a linha se o filtro não for "todos" e o status for diferente
      const esconder = situacao !== "todos" && linha.dataset.status !== situacao;
      linha.hidden = esconder;
      if (!esconder) visiveis += 1;
    });
    botoes.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.filtro === situacao)));
    semResultado.hidden = visiveis > 0;
  }

  botoes.forEach((b) => b.addEventListener("click", () => aplicar(b.dataset.filtro)));
  filtros.hidden = false;       // com JavaScript funcionando, os filtros aparecem
  aplicar("DISPONIVEL");        // começa mostrando só o que dá para pedir
}

// 2) Janela de confirmação ------------------------------------------------
const dialogo = document.getElementById("confirmacao");
if (dialogo && typeof dialogo.showModal === "function") {
  let formulario = null;        // o formulário que está esperando a confirmação

  document.querySelectorAll("form[data-confirmar]").forEach((form) => {
    form.addEventListener("submit", (evento) => {
      if (form.dataset.confirmado === "sim") return;   // já confirmado: deixa enviar
      evento.preventDefault();                         // para o envio e pergunta antes
      formulario = form;
      dialogo.querySelector("[data-titulo]").textContent = form.dataset.titulo;
      dialogo.querySelector("[data-texto]").textContent = form.dataset.confirmar;
      dialogo.querySelector("[data-sim]").textContent = form.dataset.sim;
      dialogo.querySelector("[data-nao]").textContent = form.dataset.nao;
      dialogo.showModal();
    });
  });

  dialogo.querySelector("[data-nao]").addEventListener("click", () => dialogo.close());

  dialogo.querySelector("[data-sim]").addEventListener("click", () => {
    dialogo.close();
    formulario.dataset.confirmado = "sim";
    if (formulario.requestSubmit) formulario.requestSubmit();
    else formulario.submit();
  });
}

// 3) Pop-up "faça login" ----------------------------------------------------
// Botões como "Pedir" têm o atributo data-login e um href que já leva ao /login.
// Com JavaScript, em vez de ir direto, mostramos o aviso primeiro.
const popupLogin = document.getElementById("pede-login");
if (popupLogin && typeof popupLogin.showModal === "function") {
  const irLogin = popupLogin.querySelector("[data-ir-login]");

  document.querySelectorAll("[data-login]").forEach((botao) => {
    botao.addEventListener("click", (evento) => {
      evento.preventDefault();                          // não vai direto para o login
      irLogin.setAttribute("href", botao.getAttribute("href"));  // o botão do pop-up leva ao mesmo lugar
      popupLogin.showModal();
    });
  });

  popupLogin.querySelector("[data-fechar]").addEventListener("click", () => popupLogin.close());
}

// 4) Prévia da foto escolhida no formulário de doação
const campoFoto = document.getElementById("foto");
const previa = document.getElementById("previa-foto");
if (campoFoto && previa) {
  campoFoto.addEventListener("change", () => {
    const arquivo = campoFoto.files[0];
    if (arquivo && arquivo.type.startsWith("image/")) {
      previa.src = URL.createObjectURL(arquivo);   // mostra a foto sem enviar nada ainda
      previa.hidden = false;
    } else {
      previa.hidden = true;
    }
  });
}

// 5) Chatbot de dúvidas ------------------------------------------------------
// Envia a pergunta sem recarregar a página. Sem JavaScript, o formulário
// continua funcionando: o Flask devolve a página inteira com a resposta.
const formChat = document.getElementById("form-chat");
if (formChat) {
  const conversa = document.getElementById("conversa");
  const campoPergunta = document.getElementById("pergunta");

  function mostrarMensagem(texto, autor) {
    const p = document.createElement("p");
    p.className = "mensagem mensagem-" + autor;
    p.textContent = texto;          // textContent: o texto nunca vira HTML (evita XSS)
    conversa.appendChild(p);
    p.scrollIntoView({ block: "nearest" });
  }

  formChat.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    const pergunta = campoPergunta.value.trim();
    if (!pergunta) return;

    mostrarMensagem(pergunta, "voce");
    const dados = new FormData(formChat);   // leva junto o campo csrf escondido
    campoPergunta.value = "";

    try {
      const resposta = await fetch(formChat.action, {
        method: "POST",
        body: dados,
        headers: { "Accept": "application/json" },
      });
      if (!resposta.ok) throw new Error("status " + resposta.status);
      const json = await resposta.json();
      mostrarMensagem(json.resposta, "bot");
    } catch (erro) {
      mostrarMensagem("Não consegui responder agora. Recarregue a página e tente de novo.", "bot");
    }
    campoPergunta.focus();
  });
}
