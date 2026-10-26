// alterarstatus.js
// Mostra os campos "Cliente" e "Dias de aluguel" só quando a ação
// escolhida for "Alugar". Nas outras ações (devolver / dano) eles
// não fazem sentido, então ficam escondidos.
//
// Sem JavaScript a página continua funcionando: os campos só ficam
// sempre visíveis (é o comportamento que você já tinha).

 
const radiosAcao   = document.querySelectorAll('input[name="acao"]');
const campoCliente = document.getElementById('campo-cliente');
const campoDias    = document.getElementById('campo-dias');
const selectCliente = document.getElementById('cliente');
const inputDias     = document.getElementById('dias');
 
function mostrarCampo(campo, input, visivel) {
  campo.hidden = !visivel;
 
  // Campo escondido NÃO pode ser "required": o navegador bloquearia
  // o envio do formulário por causa de um campo que o usuário nem vê.
  input.required = visivel;
 
  // Ao esconder, limpa o valor para não enviar dado velho junto.
  if (!visivel) {
    input.value = '';
  }
}
 
function atualizarCampos() {
  const escolhida = document.querySelector('input[name="acao"]:checked');
  const ehAluguel = escolhida !== null && escolhida.value === 'alugar';
 
  mostrarCampo(campoCliente, selectCliente, ehAluguel);
  mostrarCampo(campoDias, inputDias, ehAluguel);
}
 
radiosAcao.forEach(function (radio) {
  radio.addEventListener('change', atualizarCampos);
});
 
// Roda uma vez ao carregar, para já começar no estado certo.
atualizarCampos();
 
