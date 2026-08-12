# 🚗 Sistema de Aluguel de Veículos

Sistema de gerenciamento de locadora de veículos desenvolvido em Python, com cadastro de veículos, clientes, controle de aluguéis e relatórios financeiros.

## 🎯 Objetivo do projeto

Praticar, de forma aplicada, os conceitos de lógica de programação e orientação a objetos aprendidos no início da graduação em Programação de Computadores, simulando o controle real de uma locadora: cadastro de frota, gestão de clientes, processo de aluguel/devolução e acompanhamento financeiro — tudo via terminal, com persistência dos dados em arquivos.

## 📋 Funcionalidades

- Cadastrar, editar, listar e remover veículos
- Cadastrar, editar, listar e remover clientes
- Alugar e devolver veículos com cálculo automático do valor total
- Controle de veículos danificados
- Filtrar frota por status (disponível, alugado, danificado)
- Buscar veículo por placa e cliente por CPF
- Histórico de aluguéis com total arrecadado
- Consulta financeira por cliente
- Dados salvos automaticamente em arquivos JSON

## 🛠️ Tecnologias utilizadas

- **Python 3** — lógica do sistema, classes e funções
- **JSON** — persistência de dados (frota, clientes e aluguéis)

## ▶️ Como executar

```bash
git clone https://github.com/leonardoseverino423/sistema-aluguel-veiculos.git
cd sistema-aluguel-veiculos
python sistema_aluguel.py
```

## 📁 Arquivos gerados

| Arquivo | Conteúdo |
|---|---|
| `frota.json` | Veículos cadastrados |
| `clientes.json` | Clientes cadastrados |
| `alugueis.json` | Histórico de aluguéis |

## 📚 Aprendizados

Este foi meu primeiro projeto completo, desenvolvido durante o 1º período da faculdade. Na prática, ele me ajudou a consolidar:

- **Orientação a objetos**: modelagem das entidades `Veiculo`, `Cliente` e `Aluguel`, com métodos `to_dict()`/`from_dict()` para conversão entre objetos e dados persistidos.
- **Persistência de dados**: leitura e escrita em arquivos JSON, incluindo tratamento de erros de leitura (`JSONDecodeError`).
- **Validação de entradas**: garantir que placas e CPFs não se dupliquem, e tratar entradas inválidas do usuário sem quebrar o programa.
- **Organização de código**: separar responsabilidades em funções pequenas e específicas, facilitando manutenção e leitura.
- **Lógica de negócio real**: calcular valores de aluguel, controlar status de disponibilidade e gerar relatórios financeiros simples.

Ainda é um projeto de estudo, mas representa um marco importante no início da minha jornada como desenvolvedor.

## 👨‍💻 Autor

**Leonardo Severino** — projeto desenvolvido durante o 1º período da faculdade.
