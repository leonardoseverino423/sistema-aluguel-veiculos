// condicional.js
// Mostra ou esconde blocos do formulário conforme a opção escolhida em
// outro campo. Substitui o antigo alterarstatus.js e serve para qualquer
// página (alterar status, inspeção semanal, etc.).
//
// COMO USAR NO HTML
//   <div data-mostrar-quando="acao=alugar"> ... </div>
//       -> aparece só quando o campo de nome "acao" estiver com o valor "alugar"
//
//   <div data-mostrar-quando="acao=devolver,dano"> ... </div>
//       -> aparece quando o valor for "devolver" OU "dano"
//
//   <input data-obrigatorio ...>
//       -> o campo só é "required" enquanto o bloco dele estiver visível
//
// Blocos podem ficar dentro de outros blocos (ex.: o custo do óleo fica
// dentro do bloco "devolver"): o bloco de dentro só aparece se o de fora
// também estiver visível.
//
// Sem JavaScript a página continua funcionando: tudo fica visível e os
// campos só deixam de ser obrigatórios no navegador (o Python valida).

const blocos = document.querySelectorAll('[data-mostrar-quando]');

// Valor escolhido hoje no campo "nome" (radio marcado, select ou input).
function valorAtual(nome) {
  const marcado = document.querySelector('input[name="' + nome + '"]:checked');
  if (marcado) {
    return marcado.value;
  }
  const campo = document.querySelector(
    'select[name="' + nome + '"], ' +
    'input[name="' + nome + '"]:not([type="radio"]):not([type="checkbox"])'
  );
  return campo ? campo.value : null;
}

function atualizarBlocos() {
  // querySelectorAll devolve os blocos na ordem do HTML, então um bloco
  // de fora sempre é atualizado antes dos que estão dentro dele.
  blocos.forEach(function (bloco) {
    const partes = bloco.dataset.mostrarQuando.split('=');
    const nome   = partes[0];
    const aceitos = partes[1].split(',');

    const pai = bloco.parentElement.closest('[data-mostrar-quando]');
    const paiOculto = pai !== null && pai.hidden;

    const visivel = !paiOculto && aceitos.includes(valorAtual(nome));
    bloco.hidden = !visivel;

    bloco.querySelectorAll('input, select, textarea').forEach(function (campo) {
      // Se o validacao.js já marcou este campo com uma mensagem de erro,
      // limpa: senão um campo escondido continuaria bloqueando o envio.
      campo.setCustomValidity('');
      // Campo escondido NÃO pode ser "required": o navegador bloquearia
      // o envio por causa de um campo que o usuário nem vê.
      if (campo.hasAttribute('data-obrigatorio')) {
        campo.required = visivel;
      }
      // Ao esconder, limpa texto e números para não enviar dado velho.
      // (Opções de radio e caixas de marcar mantêm a escolha.)
      if (!visivel && campo.type !== 'radio' && campo.type !== 'checkbox') {
        campo.value = '';
      }
    });
  });
}

// Qualquer mudança em qualquer campo reavalia os blocos.
document.addEventListener('change', atualizarBlocos);

// Roda uma vez ao carregar, para já começar no estado certo.
atualizarBlocos();