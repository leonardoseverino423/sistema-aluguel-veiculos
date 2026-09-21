import json
import os

print("--- Programa para Aluguel de Carros ---\n")

ARQUIVO_FROTA    = "frota.json"
ARQUIVO_CLIENTES = "clientes.json"
ARQUIVO_ALUGUEIS = "alugueis.json"

#  CLASSES 

class Veiculo:
    """Representa um veículo da locadora."""
# funçao para inicializar os atributos do veículo.
    def __init__(self, marca, modelo, ano, cor, placa,
                 quilometragem, renavam, preco_dia,
                 alugado=False, danificado=False,
                 cliente=None, dias_aluguel=0):

        self.marca         = marca
        self.modelo        = modelo
        self.ano           = ano
        self.cor           = cor
        self.placa         = placa
        self.quilometragem = quilometragem
        self.renavam       = renavam
        self.preco_dia     = preco_dia
        self.alugado       = alugado
        self.danificado    = danificado
        self.cliente       = cliente
        self.dias_aluguel  = dias_aluguel

    def exibir(self):
        if self.danificado:
            status = "INDISPONÍVEL"
        elif self.alugado:
            status = "ALUGADO"
        else:
            status = "DISPONÍVEL"

        status_dano  = "| ⚠️ DANIFICADO" if self.danificado else ""
        cliente_info = f"| Cliente: {self.cliente}" if self.cliente else ""

        print(
            f"{self.marca} {self.modelo} ({self.ano}) | "
            f"Cor: {self.cor} | "
            f"Placa: {self.placa} | "
            f"KM: {self.quilometragem} | "
            f"Renavam: {self.renavam} | "
            f"R$ {self.preco_dia:.2f}/dia | "
            f"{status}{cliente_info}{status_dano}"
        )

# função para converter o objeto Veiculo em um dicionário, útil para salvar em JSON
    def to_dict(self):
        return self.__dict__ # retorna um dicionário com todos os atributos do objeto

    @staticmethod # método estático que cria um objeto Veiculo a partir de um dicionário
    def from_dict(d): 
        return Veiculo(
            marca         = d.get("marca", ""),
            modelo        = d.get("modelo", ""),
            ano           = d.get("ano", ""),
            cor           = d.get("cor", ""),
            placa         = d.get("placa", ""),
            quilometragem = d.get("quilometragem", ""),
            renavam       = d.get("renavam", ""),
            preco_dia     = d.get("preco_dia", 0.0),
            alugado       = d.get("alugado", False),
            danificado    = d.get("danificado", False),
            cliente       = d.get("cliente", None),
            dias_aluguel  = d.get("dias_aluguel", 0),
        )


class Cliente:
    """Representa um cliente da locadora."""
# função para inicializar os atributos do cliente.
    def __init__(self, nome, cpf, cnh, telefone, endereco):
        self.nome     = nome
        self.cpf      = cpf
        self.cnh      = cnh
        self.telefone = telefone
        self.endereco = endereco

    def exibir(self):
        print(
            f"Nome: {self.nome} | "
            f"CPF: {self.cpf} | "
            f"CNH: {self.cnh} | "
            f"Tel: {self.telefone} | "
            f"Endereço: {self.endereco}"
        )
# função para converter o objeto Cliente em um dicionário, útil para salvar em JSON
    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(d):
        return Cliente(
            nome     = d.get("nome", ""),
            cpf      = d.get("cpf", ""),
            cnh      = d.get("cnh", ""),
            telefone = d.get("telefone", ""),
            endereco = d.get("endereco", ""),
        )


class Aluguel:
    """Registra um aluguel realizado, incluindo cliente, veículo, dias e valor total."""
# função para inicializar os atributos do aluguel.
    def __init__(self, cliente_nome, cliente_cpf, veiculo_placa,
                 veiculo_descricao, dias, preco_dia, total):
        self.cliente_nome      = cliente_nome
        self.cliente_cpf       = cliente_cpf
        self.veiculo_placa     = veiculo_placa
        self.veiculo_descricao = veiculo_descricao
        self.dias              = dias
        self.preco_dia         = preco_dia
        self.total             = total

    def exibir(self):
        print(
            f"Cliente: {self.cliente_nome} (CPF: {self.cliente_cpf}) | "
            f"Veículo: {self.veiculo_descricao} | "
            f"Placa: {self.veiculo_placa} | "
            f"{self.dias} dia(s) x R$ {self.preco_dia:.2f} = "
            f"R$ {self.total:.2f}"
        )

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(d):
        return Aluguel(
            cliente_nome      = d.get("cliente_nome", ""),
            cliente_cpf       = d.get("cliente_cpf", ""),
            veiculo_placa     = d.get("veiculo_placa", ""),
            veiculo_descricao = d.get("veiculo_descricao", ""),
            dias              = d.get("dias", 0),
            preco_dia         = d.get("preco_dia", 0.0),
            total             = d.get("total", 0.0),
        )



#  LISTA DOS VEÍCULOS, CLIENTES E ALUGUÉIS PARA ARMAZENAR OS DADOS EM MEMÓRIA


frota    = []
clientes = []
alugueis = []



#  PERSISTÊNCIA (JSON) SIGNIFICA QUE SALVAR E CARREGAR OS DADOS EM ARQUIVOS
# ─────────────────────────────────────────
# função para salvar a frota de veículos em um arquivo JSON

def salvar_frota():
    with open(ARQUIVO_FROTA, "w", encoding="utf-8") as f: # abre o arquivo em modo de escrita, criando-o se não existir
        json.dump([v.to_dict() for v in frota], f, ensure_ascii=False, indent=2)

def carregar_frota():
    if os.path.exists(ARQUIVO_FROTA):
        with open(ARQUIVO_FROTA, "r", encoding="utf-8") as f:
            try:
                for d in json.load(f):
                    frota.append(Veiculo.from_dict(d))
            except json.JSONDecodeError:
                pass

def salvar_clientes():
    with open(ARQUIVO_CLIENTES, "w", encoding="utf-8") as f:
        json.dump([c.to_dict() for c in clientes], f, ensure_ascii=False, indent=2)

def carregar_clientes():
    if os.path.exists(ARQUIVO_CLIENTES):
        with open(ARQUIVO_CLIENTES, "r", encoding="utf-8") as f:
            try:
                for d in json.load(f):
                    clientes.append(Cliente.from_dict(d))
            except json.JSONDecodeError:
                pass

# função para salvar os registros de aluguéis em um arquivo JSON
def salvar_alugueis():
    with open(ARQUIVO_ALUGUEIS, "w", encoding="utf-8") as f:
        json.dump([a.to_dict() for a in alugueis], f, ensure_ascii=False, indent=2)

def carregar_alugueis():
    if os.path.exists(ARQUIVO_ALUGUEIS):
        with open(ARQUIVO_ALUGUEIS, "r", encoding="utf-8") as f:
            try:
                for d in json.load(f):
                    alugueis.append(Aluguel.from_dict(d))
            except json.JSONDecodeError:
                pass

#  FUNÇÕES DE LEITURA DE DADOS PARA O USUÁRIO
# funções para ler dados do usuário, garantindo que sejam válidos e não vazios

def ler_texto_obrigatorio(mensagem): 
    while True:
        valor = input(mensagem).strip() # 
        if valor:
            return valor
        print("Este campo não pode ficar vazio.\n")

def ler_float(mensagem):
    while True:
        try:
            return float(input(mensagem))
        except ValueError:
            print("Digite um valor numérico válido.\n")

def ler_int(mensagem):
    while True:
        try:
            return int(input(mensagem))
        except ValueError:
            print("Digite um número inteiro válido.\n")


# ─────────────────────────────────────────
#  VEÍCULOS 
# ─────────────────────────────────────────

# função para verificar se a placa já existe na frota, ignorando o índice do veículo atual ao editar
def placa_existe(placa, ignorar_idx=None): #ignorar_idx é usado para não comparar com o próprio veículo ao editar
    for i, v in enumerate(frota): 
        if v.placa.upper() == placa.upper() and i != ignorar_idx: #ignorar_idx é usado para não comparar com o próprio veículo ao editar
            return True
    return False

#funçao para cadastrar um novo veículo na frota
def cadastrar_veiculo():
    marca         = ler_texto_obrigatorio("Marca: ")
    modelo        = ler_texto_obrigatorio("Modelo: ")
    ano           = ler_texto_obrigatorio("Ano: ")
    cor           = ler_texto_obrigatorio("Cor: ")
    quilometragem = ler_texto_obrigatorio("Quilometragem: ")
    renavam       = ler_texto_obrigatorio("Renavam: ")

    while True:
        placa = ler_texto_obrigatorio("Placa: ").upper() #upper() para padronizar a placa em maiúsculas
        if placa_existe(placa):
            print("Já existe um veículo com essa placa.\n")
        else:
            break

    preco_dia = ler_float("Preço por dia (R$): ")
    frota.append(Veiculo(marca, modelo, ano, cor, placa,
                         quilometragem, renavam, preco_dia))
    salvar_frota()
    print("Veículo cadastrado!\n")

#função para listar todos os veículos cadastrados na frota
def listar_veiculos():
    if not frota:      # verifica se a lista de veículos está vazia
        print("Nenhum veículo cadastrado.\n")
        return
    print("\n--- Frota ---")
    for i, v in enumerate(frota):
        print(f"[{i}]", end=" ")
        v.exibir()
    print()

#função para editar os dados de um veículo existente na frota
def editar_veiculo():
    listar_veiculos()
    if not frota:
        return
    try:
        idx     = int(input("Número do veículo para editar: "))
        veiculo = frota[idx]    # seleciona o veículo pelo índice fornecido pelo usuário
    except (ValueError, IndexError): # trata erros de conversão de tipo e índice fora do intervalo da lista
        print("Opção inválida.\n")
        return

    print("\nDeixe em branco para manter o valor atual.")

#função auxiliar para atualizar os atributos do veículo, mantendo o valor atual se o usuário não digitar nada
    def atualizar(prompt, atual):
        novo = input(f"{prompt} [{atual}]: ").strip()
        return novo if novo else atual

    veiculo.marca         = atualizar("Marca",         veiculo.marca)
    veiculo.modelo        = atualizar("Modelo",        veiculo.modelo)
    veiculo.ano           = atualizar("Ano",           veiculo.ano)
    veiculo.cor           = atualizar("Cor",           veiculo.cor)
    veiculo.quilometragem = atualizar("Quilometragem", veiculo.quilometragem)
    veiculo.renavam       = atualizar("Renavam",       veiculo.renavam)

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
            print("Valor inválido, preço não alterado.")

    salvar_frota()
    print("Veículo atualizado!\n")

# função para remover um veículo da frota, com confirmação do usuário
def remover_veiculo():
    listar_veiculos()
    if not frota:
        return
    try:
        idx      = int(input("Número do veículo para remover: "))
        veiculo  = frota[idx]
        confirma = input(f"Remover {veiculo.marca} {veiculo.modelo} "
                         f"- {veiculo.placa}? (s/n): ")
        if confirma.lower() == "s":
            frota.pop(idx)
            salvar_frota()
            print("Veículo removido!\n")
        else:
            print("Remoção cancelada.\n")
    except (ValueError, IndexError):
        print("Opção inválida.\n")

# função para buscar um veículo na frota pelo número da placa, exibindo suas informações se encontrado
def buscar_por_placa():
    placa = ler_texto_obrigatorio("Digite a placa: ").upper()
    for v in frota:
        if v.placa.upper() == placa:
            v.exibir()
            return
    print("Veículo não encontrado.\n")

# função para filtrar veículos por status (disponível, alugado ou danificado) e exibir os resultados
def filtrar_veiculos():
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

# função para alterar o status de um veículo (alugado ou danificado), com verificações de disponibilidade e registro de aluguel
def alterar_status():
    listar_veiculos()
    if not frota:
        return
    try:
        idx     = int(input("Número do veículo: ")) # idx é o índice do veículo na lista frota
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
                listar_clientes()
                if not clientes:
                    print("Cadastre um cliente antes de alugar.\n")
                    return
                idx_c   = int(input("Número do cliente: "))
                cliente = clientes[idx_c]

                veiculo.dias_aluguel = ler_int("Quantos dias de aluguel? ")
                total                = veiculo.preco_dia * veiculo.dias_aluguel
                veiculo.alugado      = True
                veiculo.cliente      = cliente.nome

                registro = Aluguel(
                    cliente_nome      = cliente.nome,
                    cliente_cpf       = cliente.cpf,
                    veiculo_placa     = veiculo.placa,
                    veiculo_descricao = f"{veiculo.marca} {veiculo.modelo} ({veiculo.ano})",
                    dias              = veiculo.dias_aluguel,
                    preco_dia         = veiculo.preco_dia,
                    total             = total,
                )
                alugueis.append(registro)
                salvar_alugueis()

                print(f"\nVeículo alugado para {cliente.nome} "
                      f"por {veiculo.dias_aluguel} dia(s).")
                print(f"Valor por dia:  R$ {veiculo.preco_dia:.2f}")
                print(f"Total a pagar:  R$ {total:.2f}\n")

            else:
                # ── Devolver ──
                total = veiculo.preco_dia * veiculo.dias_aluguel
                print(f"\nDevolução de {veiculo.cliente}")
                print(f"Valor por dia:  R$ {veiculo.preco_dia:.2f}")
                print(f"Dias alugados:  {veiculo.dias_aluguel}")
                print(f"Total cobrado:  R$ {total:.2f}")
                veiculo.alugado      = False
                veiculo.cliente      = None
                veiculo.dias_aluguel = 0
                print("Veículo devolvido com sucesso!\n")

        elif opcao == "2":
            veiculo.danificado = not veiculo.danificado
            novo = "DANIFICADO" if veiculo.danificado else "SEM DANOS"
            if veiculo.danificado:
                veiculo.alugado      = False
                veiculo.cliente      = None
                veiculo.dias_aluguel = 0
                print("Aluguel cancelado automaticamente.")
            print(f"Status atualizado: {novo}\n")

        else:
            print("Opção inválida.\n")
            return

        salvar_frota()

    except (ValueError, IndexError):
        print("Opção inválida.\n")


# ─────────────────────────────────────────
#  CADASTRO DE CLIENTES E CONSULTA 
# ─────────────────────────────────────────
# função para verificar se o CPF já existe na lista de clientes, ignorando o índice do cliente atual ao editar
def cpf_existe(cpf, ignorar_idx=None):
    for i, c in enumerate(clientes):
        if c.cpf == cpf and i != ignorar_idx:
            return True
    return False

# função para cadastrar um novo cliente
def cadastrar_cliente():
    nome     = ler_texto_obrigatorio("Nome: ")
    while True:
        cpf  = ler_texto_obrigatorio("CPF: ")
        if cpf_existe(cpf):
            print("Já existe um cliente com esse CPF.\n")
        else:
            break
    cnh      = ler_texto_obrigatorio("CNH: ")
    telefone = ler_texto_obrigatorio("Telefone: ")
    endereco = ler_texto_obrigatorio("Endereço: ")

    clientes.append(Cliente(nome, cpf, cnh, telefone, endereco))
    salvar_clientes()
    print("Cliente cadastrado!\n")

# função para listar todos os clientes cadastrados
def listar_clientes():
    if not clientes:
        print("Nenhum cliente cadastrado.\n")
        return
    print("\n--- Clientes ---")
    for i, c in enumerate(clientes):
        print(f"[{i}]", end=" ")
        c.exibir()
    print()
# função para editar os dados de um cliente existente
def editar_cliente():
    listar_clientes()
    if not clientes:
        return
    try:
        idx     = int(input("Número do cliente para editar: "))
        cliente = clientes[idx]
    except (ValueError, IndexError):
        print("Opção inválida.\n")
        return

    print("\nDeixe em branco para manter o valor atual.")

# função auxiliar para atualizar os atributos do cliente, mantendo o valor atual se o usuário não digitar nada
    def atualizar(prompt, atual):
        novo = input(f"{prompt} [{atual}]: ").strip()
        return novo if novo else atual

    cliente.nome     = atualizar("Nome",     cliente.nome)
    cliente.cnh      = atualizar("CNH",      cliente.cnh)
    cliente.telefone = atualizar("Telefone", cliente.telefone)
    cliente.endereco = atualizar("Endereço", cliente.endereco)

    while True:
        novo_cpf = input(f"CPF [{cliente.cpf}]: ").strip()
        if not novo_cpf:
            break
        if cpf_existe(novo_cpf, ignorar_idx=idx):
            print("Já existe outro cliente com esse CPF.\n")
        else:
            cliente.cpf = novo_cpf
            break

    salvar_clientes()
    print("Cliente atualizado!\n")

# função para remover um cliente da lista, com confirmação do usuário
def remover_cliente():
    listar_clientes()
    if not clientes:
        return
    try:
        idx      = int(input("Número do cliente para remover: "))
        cliente  = clientes[idx]
        confirma = input(f"Remover {cliente.nome} - CPF {cliente.cpf}? (s/n): ")
        if confirma.lower() == "s":
            clientes.pop(idx)
            salvar_clientes()
            print("Cliente removido!\n")
        else:
            print("Remoção cancelada.\n")
    except (ValueError, IndexError):
        print("Opção inválida.\n")

# função para buscar um cliente na lista pelo número do CPF, exibindo suas informações se encontrado
def buscar_cliente_por_cpf():
    cpf = ler_texto_obrigatorio("Digite o CPF: ")
    for c in clientes:
        if c.cpf == cpf:
            c.exibir()
            return
    print("Cliente não encontrado.\n")


# ─────────────────────────────────────────
#  FINANCEIRO
# ─────────────────────────────────────────
# função para exibir o histórico de todos os aluguéis realizados, com total arrecadado
def relatorio_alugueis():
    if not alugueis:
        print("Nenhum aluguel registrado.\n")
        return

    print("\n--- Histórico de Aluguéis ---")
    total_geral = 0.0   # variável para acumular o total arrecadado
    for i, a in enumerate(alugueis): 
        print(f"[{i}]", end=" ")   # exibe o índice do aluguel
        a.exibir()                # exibe as informações do aluguel
        total_geral += a.total    # acumula o total arrecadado

    print(f"\nTotal arrecadado: R$ {total_geral:.2f}\n")

# função para exibir o histórico de aluguéis de um cliente específico, filtrando pelo CPF e mostrando o total pago
def relatorio_por_cliente():
    cpf       = ler_texto_obrigatorio("CPF do cliente: ")
    resultado = [a for a in alugueis if a.cliente_cpf == cpf]

    if not resultado:
        print("Nenhum aluguel encontrado para esse CPF.\n")
        return

    print(f"\n--- Aluguéis de {resultado[0].cliente_nome} ---")
    total = 0.0
    for a in resultado:
        a.exibir()
        total += a.total       # acumula o total pago pelo cliente
    print(f"\nTotal pago: R$ {total:.2f}\n")


# ─────────────────────────────────────────
#  INICIALIZAÇÃO E MENU
# ─────────────────────────────────────────

carregar_frota()
carregar_clientes()
carregar_alugueis()

while True:
    print("╔══════════════════════════════════╗")
    print("║    LOCADORA — MENU PRINCIPAL     ║")
    print("╠══════════════════════════════════╣")
    print("║  VEÍCULOS                        ║")
    print("║  1  - Cadastrar veículo          ║")
    print("║  2  - Listar frota               ║")
    print("║  3  - Alterar status             ║")
    print("║  4  - Editar veículo             ║")
    print("║  5  - Remover veículo            ║")
    print("║  6  - Buscar por placa           ║")
    print("║  7  - Filtrar veículos           ║")
    print("╠══════════════════════════════════╣")
    print("║  CLIENTES                        ║")
    print("║  8  - Cadastrar cliente          ║")
    print("║  9  - Listar clientes            ║")
    print("║  10 - Editar cliente             ║")
    print("║  11 - Remover cliente            ║")
    print("║  12 - Buscar por CPF             ║")
    print("╠══════════════════════════════════╣")
    print("║  FINANCEIRO                      ║")
    print("║  13 - Histórico de aluguéis      ║")
    print("║  14 - Consultar por cliente      ║")
    print("╠══════════════════════════════════╣")
    print("║  0  - Sair                       ║")
    print("╚══════════════════════════════════╝")

    opcao = input("Escolha: ")

    if   opcao == "1":  cadastrar_veiculo()
    elif opcao == "2":  listar_veiculos()
    elif opcao == "3":  alterar_status()
    elif opcao == "4":  editar_veiculo()
    elif opcao == "5":  remover_veiculo()
    elif opcao == "6":  buscar_por_placa()
    elif opcao == "7":  filtrar_veiculos()
    elif opcao == "8":  cadastrar_cliente()
    elif opcao == "9":  listar_clientes()
    elif opcao == "10": editar_cliente()
    elif opcao == "11": remover_cliente()
    elif opcao == "12": buscar_cliente_por_cpf()
    elif opcao == "13": relatorio_alugueis()
    elif opcao == "14": relatorio_por_cliente()
    elif opcao == "0":
        print("Dados salvos. Até logo!")
        break
    else:
        print("Opção inválida.\n")