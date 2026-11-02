// datas.js
// Impede escolher uma data futura nos campos marcados com data-max-hoje
// (ex.: data da infração de uma multa: não faz sentido ser amanhã).
//
// Uso no HTML:  <input type="date" data-max-hoje ...>
//

(function () {
  const agora = new Date();

  // Monta aaaa-mm-dd com a data LOCAL (toISOString usaria o horário UTC
  // e, à noite no Brasil, já devolveria o dia seguinte).
  const mes = String(agora.getMonth() + 1).padStart(2, '0');
  const dia = String(agora.getDate()).padStart(2, '0');
  const hoje = agora.getFullYear() + '-' + mes + '-' + dia;

  document.querySelectorAll('input[data-max-hoje]').forEach(function (campo) {
    campo.max = hoje;
  });
})();