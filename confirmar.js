// confirmar.js
// Pede confirmação antes de enviar qualquer formulário que tenha o
// atributo data-confirmar. Reproduz o "(s/n)" que o seu Python já faz
// antes de remover um veículo ou cliente.
//
// Uso no HTML:
//   <form data-confirmar="Tem certeza que deseja excluir este veículo?">
//
// Um único arquivo serve para removerveiculo.html, removercliente.html
// e qualquer outra página que precise de confirmação.

document.querySelectorAll('form[data-confirmar]').forEach(function (form) {
  form.addEventListener('submit', function (evento) {
    const mensagem = form.dataset.confirmar;

    // confirm() devolve true (OK) ou false (Cancelar).
    // Se cancelou, impede o envio do formulário.
    if (!window.confirm(mensagem)) {
      evento.preventDefault();
    }
  });
});