// validacao.js
// Traduz para português as mensagens de validação dos formulários
// ("Please fill out this field", "Please select an item in the list" etc.).
//
// Essas mensagens vêm do navegador e aparecem no idioma configurado nele,
// não no do site. Este arquivo troca o texto sem mudar as regras: continuam
// valendo os atributos required, pattern, minlength etc. do próprio HTML.
//
// Uso: <script src="validacao.js"></script> antes do </body>, em toda página com formulário.

function mensagemPara(campo) {
  const v = campo.validity;

  if (v.valueMissing) {
    if (campo.type === 'radio')    return 'Selecione uma das opções.';
    if (campo.type === 'checkbox') return 'Marque esta caixa para continuar.';
    if (campo.tagName === 'SELECT') return 'Selecione uma opção da lista.';
    return 'Preencha este campo.';
  }
  if (v.typeMismatch) {
    if (campo.type === 'email') return 'Digite um e-mail válido, como nome@exemplo.com.';
    if (campo.type === 'url')   return 'Digite um endereço válido, começando com http:// ou https://.';
    return 'O valor digitado não é válido.';
  }
  if (v.patternMismatch) {
    // O atributo title do campo explica o formato esperado (ex.: "Use 11 dígitos").
    return campo.title || 'O formato digitado não é válido.';
  }
  if (v.tooShort)       return 'Digite pelo menos ' + campo.minLength + ' caracteres.';
  if (v.tooLong)        return 'Digite no máximo ' + campo.maxLength + ' caracteres.';
  if (v.rangeUnderflow) return 'O valor deve ser maior ou igual a ' + campo.min + '.';
  if (v.rangeOverflow)  return 'O valor deve ser menor ou igual a ' + campo.max + '.';
  if (v.stepMismatch)   return 'Digite um valor válido.';
  if (v.badInput)       return 'Digite um valor válido.';
  return '';
}

document.querySelectorAll('input, select, textarea').forEach(function (campo) {
  // Disparado quando o formulário é enviado e o campo está inválido.
  campo.addEventListener('invalid', function () {
    campo.setCustomValidity('');                 // limpa para recalcular
    campo.setCustomValidity(mensagemPara(campo));
  });

  // Ao corrigir o campo, remove a mensagem personalizada;
  // senão ele continuaria "inválido" mesmo depois de preenchido.
  ['input', 'change'].forEach(function (evento) {
    campo.addEventListener(evento, function () {
      campo.setCustomValidity('');
    });
  });
});