import json
import os

print("--- Programa para Aluguel de Carros ---\n")

ARQUIVO_DADOS = "frota.json"


class Veiculo:
    """
    Representa um veículo de uma locadora.

    Cada veículo possui informações como marca,
    modelo, ano, placa, quilometragem, renavam,
    preço da diária e status.
    """

    def __init__(self, marca, modelo, ano, cor, placa,
                 quilometragem, renavam, preco_dia,
                 alugado=False, danificado=False):

        self.marca = marca
        self.modelo = modelo
        self.ano = ano
        self.cor = cor
        self.placa = placa
        self.quilometragem = quilometragem
        self.renavam = renavam
        self.preco_dia = preco_dia
        self.alugado = alugado
        self.danificado = danificado

    def exibir(self):
        if self.danificado:
            status = "INDISPONÍVEL"
        elif self.alugado:
            status = "ALUGADO"
        else:
            status = "DISPONÍVEL"

        status_dano = " | ⚠️ DANIFICADO" if self.danificado else ""

        print(
            f"{self.marca} {self.modelo} ({self.ano}) | "
            f"Cor: {self.cor} | "
            f"Placa: {self.placa} | "
            f"KM: {self.quilometragem} | "
            f"Renavam: {self.renavam} | "
            f"R$ {self.preco_dia:.2f}/dia | "
            f"{status}{status_dano}"
        )

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(d):
        return Veiculo(
            marca=d.get("marca", ""),
            modelo=d.get("modelo", ""),
            ano=d.get("ano", ""),
            cor=d.get("cor", ""),
            placa=d.get("placa", ""),
            quilometragem=d.get("quilometragem", ""),
            renavam=d.get("renavam", ""),
            preco_dia=d.get("preco_dia", 0.0),
            alugado=d.get("alugado", False),
            danificado=d.get("danificado", False),
        )


class Cliente:
    """
    Representa um cliente da locadora.
    """

    def __init__(self, nome, cpf, cnh, telefone, endereco):
        self.nome = nome
        self.cpf = cpf
        self.cnh = cnh
        self.telefone = telefone
        self.endereco = endereco


frota = []
clientes = []


# Funções auxiliares para ler entradas do usuário com validação
def salvar_dados():
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump([v.to_dict() for v in frota], f, ensure_ascii=False, indent=2)

# Função para carregar os dados da frota do arquivo JSON
def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
            try:
                dados = json.load(f)
                for d in dados:
                    frota.append(Veiculo.from_dict(d))
            except json.JSONDecodeError:
                pass  # arquivo vazio ou corrompido, ignora



# Funções auxiliares para ler entradas do usuário com validação
def ler_texto_obrigatorio(mensagem):
    while True:
        valor = input(mensagem).strip()
        if valor:
            return valor
        print("Este campo não pode ficar vazio.\n")

# Funções auxiliares para ler entradas do usuário com validação
def ler_float(mensagem):
    while True:
        try:
            return float(input(mensagem))
        except ValueError:
            print("Digite um valor válido.\n")

# Funções auxiliares para ler entradas do usuário com validação
def ler_int(mensagem):
    while True:
        try:
            return int(input(mensagem))
        except ValueError:
            print("Digite um número válido.\n")

# Função para verificar se uma placa já existe na frota
def placa_existe(placa, ignorar_idx=None):
    for i, v in enumerate(frota):
        if v.placa.upper() == placa.upper() and i != ignorar_idx:
            return True
    return False


# função para cadastrar o veículo
def cadastrar_veiculo():
    marca = ler_texto_obrigatorio("Marca: ")
    modelo = ler_texto_obrigatorio("Modelo: ")
    ano = ler_texto_obrigatorio("Ano: ")
    cor = ler_texto_obrigatorio("Cor: ")
    quilometragem = ler_texto_obrigatorio("Quilometragem: ")
    renavam = ler_texto_obrigatorio("Renavam: ")

    while True:
        placa = ler_texto_obrigatorio("Placa: ").upper()
        if placa_existe(placa):
            print("Já existe um veículo cadastrado com essa placa.\n")
        else:
            break

    preco_dia = ler_float("Preço por dia (R$): ")

    frota.append(Veiculo(marca, modelo, ano, cor, placa, quilometragem, renavam, preco_dia))
    salvar_dados()
    print("Veículo cadastrado!\n")

# função para listar todos veículos cadastrados na frota
def listar_veiculos():
    if not frota:
        print("Nenhum veículo cadastrado.\n")
        return
    print("\n--- Frota ---")
    for i, v in enumerate(frota):
        print(f"[{i}]", end=" ")
        v.exibir()
    print()

# função para remover veículos da frota.
def remover_veiculo():
    listar_veiculos()
    if not frota:
        return
    try:
        idx = int(input("Número do veículo para remover: "))
        veiculo = frota[idx]
        confirma = input(f"Tem certeza que deseja remover {veiculo.marca} {veiculo.modelo} - {veiculo.placa}? (s/n): ")
        if confirma.lower() == "s":
            frota.pop(idx)
            salvar_dados()
            print("Veículo removido com sucesso!\n")
        else:
            print("Remoção cancelada.\n")
    except (ValueError, IndexError):
        print("Opção inválida.\n")

# função para editar veículos existentes na frota
def editar_veiculo():
    listar_veiculos()
    if not frota:
        return
    try:
        idx = int(input("Número do veículo para editar: "))
        veiculo = frota[idx]
    except (ValueError, IndexError):
        print("Opção inválida.\n")
        return

    print("\nDeixe em branco para manter o valor atual.")

    nova_marca = input(f"Marca [{veiculo.marca}]: ").strip()
    if nova_marca:
        veiculo.marca = nova_marca

    novo_modelo = input(f"Modelo [{veiculo.modelo}]: ").strip()
    if novo_modelo:
        veiculo.modelo = novo_modelo

    novo_ano = input(f"Ano [{veiculo.ano}]: ").strip()
    if novo_ano:
        veiculo.ano = novo_ano

    nova_cor = input(f"Cor [{veiculo.cor}]: ").strip()
    if nova_cor:
        veiculo.cor = nova_cor

    nova_quilometragem = input(f"Quilometragem [{veiculo.quilometragem}]: ").strip()
    if nova_quilometragem:
        veiculo.quilometragem = nova_quilometragem

    novo_renavam = input(f"Renavam [{veiculo.renavam}]: ").strip()
    if novo_renavam:
        veiculo.renavam = novo_renavam

    while True:
        nova_placa = input(f"Placa [{veiculo.placa}]: ").strip().upper()
        if not nova_placa:
            break
        if placa_existe(nova_placa, ignorar_idx=idx):
            print("Já existe outro veículo com essa placa.\n")
        else:
            veiculo.placa = nova_placa
            break

    novo_preco = input(f"Preço por dia [{veiculo.preco_dia:.2f}]: ").strip()
    if novo_preco:
        try:
            veiculo.preco_dia = float(novo_preco)
        except ValueError:
            print("Valor inválido, preço não foi alterado.")

    salvar_dados()
    print("Veículo atualizado com sucesso!\n")

# função para buscar veículos da frota com base na placa.
def buscar_por_placa():
    """
    Procura um veículo na frota utilizando sua placa.
    Solicita ao usuário a placa do veículo, percorre a lista
    de veículos cadastrados e exibe as informações caso o
    veículo seja encontrado.

    Retorna:
        None
    """
    placa = input("Digite a placa: ").strip().upper() #.strip()Remove espaços no começo e no final.|#upper()Transforma tudo em letras maiúsculas.
    encontrado = False
    for v in frota:
        if v.placa.upper() == placa:
            v.exibir()
            encontrado = True
            break
    if not encontrado:
        print("Veículo não encontrado.\n")


# função para filtrar veículos da frota com base no status de disponibilidade, aluguel ou dano.
def filtrar_veiculos():
    """ 
    Filtra os veículos da frota com base no status de disponibilidade, aluguel ou dano.
    Solicita ao usuário que escolha um filtro e exibe os veículos correspondentes.
    Retorna:
        None"""
    
    print("Filtrar por:")
    print("1 - Disponíveis")
    print("2 - Alugados")
    print("3 - Danificados")
    opcao = input("Escolha: ")

    filtros = {
        "1": ("DISPONÍVEIS", lambda v: not v.alugado and not v.danificado),
        "2": ("ALUGADOS",    lambda v: v.alugado),
        "3": ("DANIFICADOS", lambda v: v.danificado),
    }

    if opcao not in filtros:
        print("Opção inválida.\n")
        return

    titulo, condicao = filtros[opcao]
    resultado = [v for v in frota if condicao(v)]

    print(f"\n--- {titulo} ---")
    if not resultado:
        print("Nenhum veículo encontrado.\n")
    else:
        for v in resultado:
            v.exibir()
    print()

# função para alterar o status de um veículo, seja para aluguel ou dano.
def alterar_status():
    listar_veiculos()
    if not frota:
        return
    try:
        idx = int(input("Número do veículo: "))
        veiculo = frota[idx]

        print("O que deseja alterar?")
        print("1 - Status de aluguel")
        print("2 - Status de dano")
        opcao = input("Escolha: ")

        if opcao == "1":
            if veiculo.danificado:
                print("Veículo danificado não pode ser alugado.\n")
                return
            if not veiculo.alugado:
                # Alugar
                veiculo.cliente = ler_texto_obrigatorio("Nome do cliente: ")
                veiculo.dias_aluguel = ler_int("Quantos dias de aluguel? ")
                total = veiculo.preco_dia * veiculo.dias_aluguel
                veiculo.alugado = True
                print(f"Veículo alugado para {veiculo.cliente} por {veiculo.dias_aluguel} dia(s).")
                print(f"Total: R${total:.2f}\n")
            else:
                # Devolver
                total = veiculo.preco_dia * veiculo.dias_aluguel
                print(f"Devolução de {veiculo.cliente} | Total cobrado: R${total:.2f}")
                veiculo.alugado = False
                veiculo.cliente = None
                veiculo.dias_aluguel = 0
                print("Veículo devolvido com sucesso!\n")

        elif opcao == "2":
            veiculo.danificado = not veiculo.danificado
            novo = "DANIFICADO" if veiculo.danificado else "SEM DANOS"
            if veiculo.danificado:
                veiculo.alugado = False
                veiculo.cliente = None
                print("Aluguel cancelado automaticamente.")
            print(f"Status atualizado: {novo}\n")

        else:
            print("Opção inválida.\n")
            return

        salvar_dados()

    except (ValueError, IndexError):
        print("Opção inválida.\n")



# Menu principal do progrma
carregar_dados()

while True:
    print("1 - Cadastrar veículo")
    print("2 - Listar frota")
    print("3 - Alterar status do veículo")
    print("4 - Editar veículo")
    print("5 - Remover veículo")
    print("6 - Buscar por placa")
    print("7 - Filtrar veículos")
    print("8 - Sair")
    opcao = input("Escolha: ")

    if opcao == "1":
        cadastrar_veiculo()
    elif opcao == "2":
        listar_veiculos()
    elif opcao == "3":
        alterar_status()
    elif opcao == "4":
        editar_veiculo()
    elif opcao == "5":
        remover_veiculo()
    elif opcao == "6":
        buscar_por_placa()
    elif opcao == "7":
        filtrar_veiculos()
    elif opcao == "8":
        print("Dados salvos. Até logo!")
        break
    else:
        print("Opção inválida.\n")
