# Sistema de Aluguel de Veículos

Sistema de gerenciamento de uma locadora de veículos, em desenvolvimento como projeto de estudo (faculdade de Ciência da Computação) e base para um futuro TCC.

> Projeto em desenvolvimento, com fins de estudo.

## O que o sistema faz

- Cadastro de veículos e de clientes
- Listagem da frota
- Busca de veículo por placa
- Filtro de veículos
- Alteração de status do veículo (alugar, devolver, registrar dano)
- Edição de cliente e remoção de veículo
- Busca de cliente por CPF, com ou sem pontos e traço

## Estrutura

- **Back-end (Python):** programa de terminal com orientação a objetos (classes de veículo, cliente e aluguel) e dados salvos em JSON.
- **Front-end (HTML, CSS e JavaScript):** páginas do sistema com tema preto e dourado. O JavaScript cuida de mostrar/ocultar campos e de pedir confirmação antes de excluir.

Por enquanto, o front-end e o back-end ainda não estão conectados.

## Como rodar o programa em Python

Requisito: Python 3.

Na pasta do projeto, execute `python3 "Locação-veiculo 0.5.py"` e siga o menu no terminal.

Para ver as páginas, abra o arquivo `index.html` no navegador.

## Próximos passos

- Conectar o front-end ao Python com Flask
- Migrar o armazenamento de JSON para um banco de dados
- Evoluir o projeto para o TCC e, depois, para um sistema web multiempresa

## Autor

Leonardo Severino
