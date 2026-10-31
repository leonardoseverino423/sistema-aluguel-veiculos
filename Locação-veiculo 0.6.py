import json
import os
import re
from datetime import date, datetime, timedelta

ARQUIVO_FROTA       = "frota.json"
ARQUIVO_CLIENTES    = "clientes.json"
ARQUIVO_ALUGUEIS    = "alugueis.json"
ARQUIVO_LANCAMENTOS = "lancamentos.json"
ARQUIVO_INSPECOES   = "inspecoes.json"


# ─────────────────────────────────────────
#  REGRAS DE NEGÓCIO (tudo que muda a regra fica aqui, em um só lugar)
# ─────────────────────────────────────────

# Regra 1: o locatário deve levar o veículo à locadora 1 vez por semana.
INTERVALO_INSPECAO_DIAS = 7

# Regra 2: quem paga cada tipo de custo.
#   manutencao -> LOCADORA  (desgaste natural: óleo, pneus, peças mecânicas)
#   avaria     -> LOCATÁRIO (amassados, riscos, quebras durante o aluguel)
#   multa      -> LOCATÁRIO (infração cometida com o veículo em posse dele)
RESPONSAVEL_POR_TIPO = {
    "manutencao": "locadora",
    "avaria":     "locatario",
    "multa":      "locatario",
}

NOME_TIPO = {
    "manutencao": "Manutenção mecânica",
    "avaria":     "Avaria/dano",
    "multa":      "Multa de trânsito",
}

NOME_RESPONSAVEL = {
    "locadora":  "Locadora",
    "locatario": "Cliente",
}

# Itens avaliados na manutenção mecânica (chave, nome exibido)
ITENS_MECANICOS = [
    ("oleo",  "Óleo (nível/troca)"),
    ("pneus", "Pneus"),
    ("pecas", "Peças mecânicas"),
]


# ─────────────────────────────────────────
#  DATAS
# ─────────────────────────────────────────

def hoje():
    """Data de hoje. Fica em uma função para facilitar testes (simular outro dia)."""
    return date.today()

def formatar_data(iso):
    """'2026-10-31' -> '31/10/2026'. Aceita vazio."""
    if not iso:
        return "—"
    return date.fromisoformat(iso).strftime("%d/%m/%Y")

def ler_data(mensagem):
    while True:
        texto = input(mensagem).strip()
        try:
            return datetime.strptime(texto, "%d/%m/%Y").date()
        except ValueError:
            print("Data inválida. Use o formato dd/mm/aaaa.\n")


#  CLASSES

def km_para_int(valor):
    """Converte a quilometragem para número inteiro.
    Aceita dados antigos salvos como texto ('15000' ou '15.000')."""
    if isinstance(valor, (int, float)):
        return int(valor)
    digitos = re.sub(r'\D', '', str(valor))
    return int(digitos) if digitos else 0


class Veiculo:
    """Representa um veículo da locadora."""
# funçao para inicializar os atributos do veículo.
    def __init__(self, marca, modelo, ano, cor, placa,
                 quilometragem, renavam, preco_dia,
                 alugado=False, danificado=False,
                 cliente=None, dias_aluguel=0,
                 aluguel_id=None, ultima_inspecao=None):

        self.marca           = marca
        self.modelo          = modelo
        self.ano             = ano
        self.cor             = cor
        self.placa           = placa
        self.quilometragem   = km_para_int(quilometragem)
        self.renavam         = renavam
        self.preco_dia       = preco_dia
        self.alugado         = alugado
        self.danificado      = danificado
        self.cliente         = cliente
        self.dias_aluguel    = dias_aluguel
        self.aluguel_id      = aluguel_id       # id do aluguel em andamento
        self.ultima_inspecao = ultima_inspecao  # data (ISO) da última inspeção ou do início do aluguel

    # Regra 1: a próxima inspeção vence 7 dias depois da última.
    def proxima_inspecao(self):
        if not self.alugado or not self.ultima_inspecao:
            return None
        return date.fromisoformat(self.ultima_inspecao) + timedelta(days=INTERVALO_INSPECAO_DIAS)

    def inspecao_atrasada(self):
        proxima = self.proxima_inspecao()
        return proxima is not None and hoje() > proxima

    def exibir(self):
        if self.danificado:
            status = "INDISPONÍVEL"
        elif self.alugado:
            status = "ALUGADO"
        else:
            status = "DISPONÍVEL"

        status_dano  = "| ⚠️ DANIFICADO" if self.danificado else ""
        cliente_info = f"| Cliente: {self.cliente}" if self.cliente else ""

        proxima = self.proxima_inspecao()
        if proxima is None:
            info_inspecao = ""
        elif self.inspecao_atrasada():
            info_inspecao = f"| ⚠️ INSPEÇÃO ATRASADA (venceu em {proxima.strftime('%d/%m/%Y')})"
        else:
            info_inspecao = f"| Próx. inspeção: {proxima.strftime('%d/%m/%Y')}"

        km = f"{self.quilometragem:,}".replace(",", ".")   # 15000 -> 15.000

        print(
            f"{self.marca} {self.modelo} ({self.ano}) | "
            f"Cor: {self.cor} | "
            f"Placa: {self.placa} | "
            f"KM: {km} | "
            f"Renavam: {self.renavam} | "
            f"R$ {self.preco_dia:.2f}/dia | "
            f"{status}{cliente_info}{status_dano}{info_inspecao}"
        )

# função para converter o objeto Veiculo em um dicionário, útil para salvar em JSON
    def to_dict(self):
        return self.__dict__ # retorna um dicionário com todos os atributos do objeto

    @staticmethod # método estático que cria um objeto Veiculo a partir de um dicionário
    def from_dict(d):
        return Veiculo(
            marca           = d.get("marca", ""),
            modelo          = d.get("modelo", ""),
            ano             = d.get("ano", ""),
            cor             = d.get("cor", ""),
            placa           = d.get("placa", ""),
            quilometragem   = d.get("quilometragem", 0),
            renavam         = d.get("renavam", ""),
            preco_dia       = d.get("preco_dia", 0.0),
            alugado         = d.get("alugado", False),
            danificado      = d.get("danificado", False),
            cliente         = d.get("cliente", None),
            dias_aluguel    = d.get("dias_aluguel", 0),
            aluguel_id      = d.get("aluguel_id", None),
            ultima_inspecao = d.get("ultima_inspecao", None),
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
    """Registra um aluguel: cliente, veículo, período e valor das diárias.
    Os custos extras (avarias, multas) ficam em Lancamento, ligados pelo id."""
# função para inicializar os atributos do aluguel.
    def __init__(self, cliente_nome, cliente_cpf, veiculo_placa,
                 veiculo_descricao, dias, preco_dia, total,
                 id=None, data_inicio=None, data_fim=None, ativo=False):
        self.id                = id
        self.cliente_nome      = cliente_nome
        self.cliente_cpf       = cliente_cpf
        self.veiculo_placa     = veiculo_placa
        self.veiculo_descricao = veiculo_descricao
        self.dias              = dias
        self.preco_dia         = preco_dia
        self.total             = total          # valor das diárias
        self.data_inicio       = data_inicio    # ISO: posse do veículo começa
        self.data_fim          = data_fim       # ISO: devolução (None = em andamento)
        self.ativo             = ativo

    def exibir(self):
        periodo = ""
        if self.data_inicio:
            fim = formatar_data(self.data_fim) if self.data_fim else "em andamento"
            periodo = f" | Período: {formatar_data(self.data_inicio)} a {fim}"
        print(
            f"Cliente: {self.cliente_nome} (CPF: {self.cliente_cpf}) | "
            f"Veículo: {self.veiculo_descricao} | "
            f"Placa: {self.veiculo_placa} | "
            f"{self.dias} dia(s) x R$ {self.preco_dia:.2f} = "
            f"R$ {self.total:.2f}{periodo}"
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
            id                = d.get("id", None),
            data_inicio       = d.get("data_inicio", None),
            data_fim          = d.get("data_fim", None),
            ativo             = d.get("ativo", False),
        )


class Lancamento:
    """Um valor financeiro com responsável definido: manutenção, avaria ou multa.
    O responsável (locadora ou locatário) é decidido por RESPONSAVEL_POR_TIPO."""
    def __init__(self, id, aluguel_id, veiculo_placa, data, tipo,
                 descricao, valor, responsavel):
        self.id            = id
        self.aluguel_id    = aluguel_id     # None = custo sem aluguel (sempre da locadora)
        self.veiculo_placa = veiculo_placa
        self.data          = data           # ISO
        self.tipo          = tipo           # manutencao | avaria | multa
        self.descricao     = descricao
        self.valor         = valor
        self.responsavel   = responsavel    # locadora | locatario

    def exibir(self):
        print(
            f"{formatar_data(self.data)} | {NOME_TIPO[self.tipo]} | "
            f"{self.veiculo_placa} | {self.descricao} | "
            f"R$ {self.valor:.2f} | Responsável: {NOME_RESPONSAVEL[self.responsavel]}"
        )

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(d):
        return Lancamento(
            id            = d.get("id"),
            aluguel_id    = d.get("aluguel_id"),
            veiculo_placa = d.get("veiculo_placa", ""),
            data          = d.get("data"),
            tipo          = d.get("tipo", "manutencao"),
            descricao     = d.get("descricao", ""),
            valor         = d.get("valor", 0.0),
            responsavel   = d.get("responsavel", "locadora"),
        )


class Inspecao:
    """Registro de uma inspeção (semanal ou de devolução)."""
    def __init__(self, id, aluguel_id, veiculo_placa, cliente_nome,
                 data, tipo, km, mecanica, avarias):
        self.id            = id
        self.aluguel_id    = aluguel_id
        self.veiculo_placa = veiculo_placa
        self.cliente_nome  = cliente_nome
        self.data          = data        # ISO
        self.tipo          = tipo        # semanal | devolucao
        self.km            = km
        self.mecanica      = mecanica    # {"oleo": "OK" ou "TROCA/REPARO", ...}
        self.avarias       = avarias     # texto ('' = sem avarias)

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(d):
        return Inspecao(
            id            = d.get("id"),
            aluguel_id    = d.get("aluguel_id"),
            veiculo_placa = d.get("veiculo_placa", ""),
            cliente_nome  = d.get("cliente_nome", ""),
            data          = d.get("data"),
            tipo          = d.get("tipo", "semanal"),
            km            = d.get("km", 0),
            mecanica      = d.get("mecanica", {}),
            avarias       = d.get("avarias", ""),
        )


# ─────────────────────────────────────────
#  LISTAS PARA ARMAZENAR OS DADOS EM MEMÓRIA
# ─────────────────────────────────────────

frota       = []
clientes    = []
alugueis    = []
lancamentos = []
inspecoes   = []


# ─────────────────────────────────────────
#  PERSISTÊNCIA (JSON) SIGNIFICA QUE SALVAR E CARREGAR OS DADOS EM ARQUIVOS
# ─────────────────────────────────────────

# funções genéricas: servem para qualquer lista de objetos com to_dict/from_dict
def salvar_lista(arquivo, lista):
    with open(arquivo, "w", encoding="utf-8") as f: # abre o arquivo em modo de escrita, criando-o se não existir
        json.dump([item.to_dict() for item in lista], f, ensure_ascii=False, indent=2)

def carregar_lista(arquivo, lista, classe):
    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            try:
                for d in json.load(f):
                    lista.append(classe.from_dict(d))
            except json.JSONDecodeError:
                pass

def salvar_frota():       salvar_lista(ARQUIVO_FROTA, frota)
def carregar_frota():     carregar_lista(ARQUIVO_FROTA, frota, Veiculo)

def salvar_clientes():    salvar_lista(ARQUIVO_CLIENTES, clientes)
def carregar_clientes():  carregar_lista(ARQUIVO_CLIENTES, clientes, Cliente)

def salvar_alugueis():    salvar_lista(ARQUIVO_ALUGUEIS, alugueis)
def carregar_alugueis():  carregar_lista(ARQUIVO_ALUGUEIS, alugueis, Aluguel)

def salvar_lancamentos():   salvar_lista(ARQUIVO_LANCAMENTOS, lancamentos)
def carregar_lancamentos(): carregar_lista(ARQUIVO_LANCAMENTOS, lancamentos, Lancamento)

def salvar_inspecoes():   salvar_lista(ARQUIVO_INSPECOES, inspecoes)
def carregar_inspecoes(): carregar_lista(ARQUIVO_INSPECOES, inspecoes, Inspecao)


def proximo_id(lista):
    """Próximo número de id livre para uma lista de objetos com atributo id."""
    return max((item.id or 0 for item in lista), default=0) + 1

def migrar_dados_antigos():
    """Ajusta arquivos salvos por versões anteriores (sem id, datas ou inspeção),
    para que aluguéis já em andamento passem a seguir as novas regras."""
    mudou = False

    for a in alugueis:
        if a.id is None:
            a.id = proximo_id(alugueis)
            mudou = True

    for v in frota:
        if v.alugado and v.aluguel_id is None:
            # liga o veículo ao último aluguel registrado para a placa dele
            candidatos = [a for a in alugueis if a.veiculo_placa.upper() == v.placa.upper()]
            if candidatos:
                aluguel = candidatos[-1]
                aluguel.ativo = True
                if not aluguel.data_inicio:
                    aluguel.data_inicio = hoje().isoformat()
                v.aluguel_id = aluguel.id
                mudou = True
        if v.alugado and not v.ultima_inspecao:
            # sem histórico: a contagem dos 7 dias começa hoje
            v.ultima_inspecao = hoje().isoformat()
            mudou = True

    if mudou:
        salvar_alugueis()
        salvar_frota()


# ─────────────────────────────────────────
#  FUNÇÕES DE LEITURA DE DADOS PARA O USUÁRIO
# ─────────────────────────────────────────

def ler_texto_obrigatorio(mensagem):
    while True:
        valor = input(mensagem).strip()
        if valor:
            return valor
        print("Este campo não pode ficar vazio.\n")

def ler_float(mensagem):
    while True:
        try:
            # aceita vírgula como separador decimal (150,50)
            return float(input(mensagem).replace(",", "."))
        except ValueError:
            print("Digite um valor numérico válido.\n")

def ler_dinheiro(mensagem):
    """Valor em reais, sem aceitar negativo."""
    while True:
        valor = ler_float(mensagem)
        if valor < 0:
            print("O valor não pode ser negativo.\n")
        else:
            return round(valor, 2)

def ler_int(mensagem):
    while True:
        try:
            return int(input(mensagem))
        except ValueError:
            print("Digite um número inteiro válido.\n")

def ler_km(mensagem):
    """Quilometragem: aceita 15000 ou 15.000."""
    while True:
        texto = input(mensagem).strip()
        if re.fullmatch(r'\d{1,3}(\.\d{3})+|\d+', texto):
            return km_para_int(texto)
        print("Digite apenas números (ex.: 15000 ou 15.000).\n")

def ler_sim_nao(mensagem):
    """Repete até o usuário digitar s ou n. Devolve True para 's'."""
    while True:
        resposta = input(mensagem).strip().lower()
        if resposta in ("s", "n"):
            return resposta == "s"
        print("Digite s para sim ou n para não.\n")


def normalizar_cpf(cpf):
    """Remove pontos, traços e qualquer caractere que não seja dígito.
    Garante que '123.456.789-00' e '12345678900' sejam tratados como o
    mesmo CPF, tanto na checagem de duplicidade quanto na busca — sem
    isso, o mesmo CPF digitado de formas diferentes escaparia de
    cpf_existe() e criaria clientes duplicados."""
    return re.sub(r'\D', '', cpf)


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
    quilometragem = ler_km("Quilometragem: ")
    renavam       = ler_texto_obrigatorio("Renavam: ")

    while True:
        placa = ler_texto_obrigatorio("Placa: ").upper() #upper() para padronizar a placa em maiúsculas
        if placa_existe(placa):
            print("Já existe um veículo com essa placa.\n")
        else:
            break

    preco_dia = ler_dinheiro("Preço por dia (R$): ")
    frota.append(Veiculo(marca, modelo, ano, cor, placa,
                         quilometragem, renavam, preco_dia))
    salvar_frota()
    print("Veículo cadastrado!\n")

#função para listar todos os veículos cadastrados na frota
def listar_veiculos():
    if not frota:
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
        veiculo = frota[idx]
    except (ValueError, IndexError):
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

    novo_km = input(f"Quilometragem [{veiculo.quilometragem}]: ").strip()
    if novo_km:
        if re.fullmatch(r'\d{1,3}(\.\d{3})+|\d+', novo_km):
            veiculo.quilometragem = km_para_int(novo_km)
        else:
            print("Valor inválido, quilometragem não alterada.")

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
            veiculo.preco_dia = float(novo_preco.replace(",", "."))
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
        if veiculo.alugado:
            print("Este veículo está alugado. Faça a devolução antes de removê-lo.\n")
            return
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


# ─────────────────────────────────────────
#  LANÇAMENTOS FINANCEIROS (quem paga o quê)
# ─────────────────────────────────────────

def buscar_aluguel(aluguel_id):
    for a in alugueis:
        if a.id == aluguel_id:
            return a
    return None

def lancar(aluguel, placa, tipo, descricao, valor, data=None):
    """Registra um custo e já define o responsável pela regra de negócio.
    Sem aluguel (ex.: multa de uma data em que o carro estava na locadora)
    não existe cliente para cobrar, então o custo fica com a locadora."""
    responsavel = RESPONSAVEL_POR_TIPO[tipo]
    if aluguel is None:
        responsavel = "locadora"

    lanc = Lancamento(
        id            = proximo_id(lancamentos),
        aluguel_id    = aluguel.id if aluguel else None,
        veiculo_placa = placa,
        data          = (data or hoje()).isoformat(),
        tipo          = tipo,
        descricao     = descricao,
        valor         = valor,
        responsavel   = responsavel,
    )
    lancamentos.append(lanc)
    salvar_lancamentos()
    return lanc

def cobrancas_do_aluguel(aluguel):
    """Custos extras que o CLIENTE paga neste aluguel (avarias e multas)."""
    return [l for l in lancamentos
            if l.aluguel_id == aluguel.id and l.responsavel == "locatario"]

def total_a_cobrar(aluguel):
    """Diárias + avarias + multas atribuídas ao cliente."""
    return round(aluguel.total + sum(l.valor for l in cobrancas_do_aluguel(aluguel)), 2)

def exibir_fatura(aluguel):
    print(f"\n--- Fatura: {aluguel.cliente_nome} (CPF {aluguel.cliente_cpf}) ---")
    print(f"Veículo: {aluguel.veiculo_descricao} | Placa: {aluguel.veiculo_placa}")
    if aluguel.data_inicio:
        fim = formatar_data(aluguel.data_fim) if aluguel.data_fim else "em andamento"
        print(f"Período: {formatar_data(aluguel.data_inicio)} a {fim}")
    print(f"Diárias:  {aluguel.dias} x R$ {aluguel.preco_dia:.2f} = R$ {aluguel.total:.2f}")
    for l in cobrancas_do_aluguel(aluguel):
        print(f"{NOME_TIPO[l.tipo]}: {l.descricao} = R$ {l.valor:.2f}")
    print(f"TOTAL A COBRAR: R$ {total_a_cobrar(aluguel):.2f}")

    tem_manutencao = any(l.aluguel_id == aluguel.id and l.tipo == "manutencao"
                         for l in lancamentos)
    if tem_manutencao:
        print("(Manutenção mecânica é custo da locadora e não entra nesta fatura.)")
    print()


# ─────────────────────────────────────────
#  INSPEÇÃO SEMANAL (Regra 1) E AVALIAÇÃO (Regra 2)
# ─────────────────────────────────────────

def realizar_inspecao(veiculo, aluguel, tipo):
    """Inspeção completa: uso (km), mecânica (locadora) e avarias (cliente).
    É usada na inspeção semanal e também na devolução do veículo."""
    titulo = "semanal" if tipo == "semanal" else "de devolução"
    print(f"\n--- Inspeção {titulo}: {veiculo.marca} {veiculo.modelo} ({veiculo.placa}) ---")
    print(f"Cliente: {aluguel.cliente_nome}\n")

    # 1. Controle de uso: a quilometragem nunca pode diminuir
    while True:
        km = ler_km("Quilometragem atual: ")
        if km < veiculo.quilometragem:
            print(f"A quilometragem não pode ser menor que a registrada "
                  f"({veiculo.quilometragem}).\n")
        else:
            break

    # 2. Manutenção mecânica: desgaste natural, custo da LOCADORA
    print("\nAvaliação mecânica (custo da LOCADORA):")
    mecanica = {}
    for chave, nome in ITENS_MECANICOS:
        precisa = ler_sim_nao(f"{nome} precisa de troca/reparo? (s/n): ")
        mecanica[chave] = "TROCA/REPARO" if precisa else "OK"
        if precisa:
            custo = ler_dinheiro(f"  Custo do serviço - {nome} (R$): ")
            lancar(aluguel, veiculo.placa, "manutencao", nome, custo)

    # 3. Avarias: amassados, riscos, quebras causados no aluguel, custo do CLIENTE
    avarias = ""
    if ler_sim_nao("\nHá avarias (amassados, riscos, quebras)? (s/n): "):
        avarias = ler_texto_obrigatorio("Descrição da avaria: ")
        valor   = ler_dinheiro("Valor a cobrar do cliente (R$): ")
        lancar(aluguel, veiculo.placa, "avaria", avarias, valor)
        print(f"Avaria cobrada de {aluguel.cliente_nome}.")
        if ler_sim_nao("Marcar o veículo como danificado (indisponível para novos aluguéis)? (s/n): "):
            veiculo.danificado = True

    # 4. Atualiza o veículo e guarda o histórico
    veiculo.quilometragem   = km
    veiculo.ultima_inspecao = hoje().isoformat()

    inspecoes.append(Inspecao(
        id            = proximo_id(inspecoes),
        aluguel_id    = aluguel.id,
        veiculo_placa = veiculo.placa,
        cliente_nome  = aluguel.cliente_nome,
        data          = hoje().isoformat(),
        tipo          = tipo,
        km            = km,
        mecanica      = mecanica,
        avarias       = avarias,
    ))
    salvar_inspecoes()
    salvar_frota()
    print("\nInspeção registrada!")

def registrar_inspecao_semanal():
    alugados = [(i, v) for i, v in enumerate(frota) if v.alugado]
    if not alugados:
        print("Nenhum veículo alugado no momento.\n")
        return

    print("\n--- Veículos alugados ---")
    for i, v in alugados:
        print(f"[{i}]", end=" ")
        v.exibir()
    print()

    try:
        veiculo = frota[int(input("Número do veículo inspecionado: "))]
    except (ValueError, IndexError):
        print("Opção inválida.\n")
        return
    if not veiculo.alugado:
        print("Este veículo não está alugado.\n")
        return

    aluguel = buscar_aluguel(veiculo.aluguel_id)
    if aluguel is None:
        print("Não foi possível localizar o registro do aluguel deste veículo.\n")
        return

    realizar_inspecao(veiculo, aluguel, "semanal")
    print(f"Próxima inspeção até {veiculo.proxima_inspecao().strftime('%d/%m/%Y')}.\n")

def inspecoes_pendentes():
    alugados = [v for v in frota if v.alugado and v.proxima_inspecao()]
    if not alugados:
        print("Nenhum veículo alugado com inspeção a acompanhar.\n")
        return

    print("\n--- Inspeções semanais ---")
    # os mais atrasados primeiro
    for v in sorted(alugados, key=lambda x: x.proxima_inspecao()):
        dias = (v.proxima_inspecao() - hoje()).days
        if dias < 0:
            situacao = f"⚠️ ATRASADA há {-dias} dia(s)"
        elif dias == 0:
            situacao = "vence HOJE"
        else:
            situacao = f"vence em {dias} dia(s)"
        print(f"{v.marca} {v.modelo} ({v.placa}) | Cliente: {v.cliente} | "
              f"Última: {formatar_data(v.ultima_inspecao)} | {situacao}")
    print()

def avisar_inspecoes_atrasadas():
    atrasadas = [v for v in frota if v.alugado and v.inspecao_atrasada()]
    if atrasadas:
        print(f"⚠️  ATENÇÃO: {len(atrasadas)} veículo(s) com inspeção semanal "
              f"atrasada (veja a opção 16).\n")


# ─────────────────────────────────────────
#  MULTAS DE TRÂNSITO (Regra 2: responsabilidade do locatário)
# ─────────────────────────────────────────

def aluguel_na_data(placa, data):
    """Aluguéis em que o veículo estava com o cliente na data da infração
    (início e fim do período contam como dentro)."""
    achados = []
    for a in alugueis:
        if a.veiculo_placa.upper() != placa.upper() or not a.data_inicio:
            continue
        inicio = date.fromisoformat(a.data_inicio)
        fim    = date.fromisoformat(a.data_fim) if a.data_fim else hoje()
        if inicio <= data <= fim:
            achados.append(a)
    return achados

def registrar_multa():
    """A multa vai para quem estava com o veículo na DATA DA INFRAÇÃO,
    mesmo que o aluguel já tenha terminado (multas chegam semanas depois)."""
    placa = ler_texto_obrigatorio("Placa do veículo multado: ").upper()
    data  = ler_data("Data da infração (dd/mm/aaaa): ")
    if data > hoje():
        print("A data da infração não pode ser futura.\n")
        return

    descricao = ler_texto_obrigatorio("Descrição ou nº do auto de infração: ")
    valor     = ler_dinheiro("Valor da multa (R$): ")

    achados = aluguel_na_data(placa, data)

    if not achados:
        print("\nNenhum aluguel cobre essa data: a multa é de responsabilidade da LOCADORA.")
        if ler_sim_nao("Registrar como despesa da locadora? (s/n): "):
            lancar(None, placa, "multa", descricao, valor, data=data)
            print("Multa registrada como despesa da locadora.\n")
        else:
            print("Nada foi registrado.\n")
        return

    if len(achados) == 1:
        aluguel = achados[0]
    else:
        print("\nMais de um aluguel cobre essa data (troca de cliente no mesmo dia):")
        for i, a in enumerate(achados):
            print(f"[{i}]", end=" ")
            a.exibir()
        try:
            aluguel = achados[int(input("Qual cliente estava com o veículo? "))]
        except (ValueError, IndexError):
            print("Opção inválida. Nada foi registrado.\n")
            return

    lancar(aluguel, placa, "multa", descricao, valor, data=data)
    print(f"\nMulta de R$ {valor:.2f} atribuída a {aluguel.cliente_nome} "
          f"(aluguel de {formatar_data(aluguel.data_inicio)}).\n")


# ─────────────────────────────────────────
#  ALTERAR STATUS: ALUGAR, DEVOLVER, DANO
# ─────────────────────────────────────────

# função para alterar o status de um veículo (alugado ou danificado), com verificações de disponibilidade e registro de aluguel
def alterar_status():
    listar_veiculos()
    if not frota:
        return
    try:
        idx     = int(input("Número do veículo: "))
        veiculo = frota[idx]

        print("O que deseja alterar?")
        print("1 - Status de aluguel")
        print("2 - Status de dano")
        opcao = input("Escolha: ")

        if opcao == "1":
            # um veículo danificado não pode ser alugado, mas se o dano aconteceu
            # durante o aluguel ele precisa poder ser devolvido normalmente
            if veiculo.danificado and not veiculo.alugado:
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

                registro = Aluguel(
                    cliente_nome      = cliente.nome,
                    cliente_cpf       = cliente.cpf,
                    veiculo_placa     = veiculo.placa,
                    veiculo_descricao = f"{veiculo.marca} {veiculo.modelo} ({veiculo.ano})",
                    dias              = veiculo.dias_aluguel,
                    preco_dia         = veiculo.preco_dia,
                    total             = total,
                    id                = proximo_id(alugueis),
                    data_inicio       = hoje().isoformat(),
                    data_fim          = None,
                    ativo             = True,
                )
                alugueis.append(registro)
                salvar_alugueis()

                veiculo.alugado         = True
                veiculo.cliente         = cliente.nome
                veiculo.aluguel_id      = registro.id
                veiculo.ultima_inspecao = hoje().isoformat()   # a contagem dos 7 dias começa aqui

                print(f"\nVeículo alugado para {cliente.nome} "
                      f"por {veiculo.dias_aluguel} dia(s).")
                print(f"Valor por dia:  R$ {veiculo.preco_dia:.2f}")
                print(f"Total das diárias:  R$ {total:.2f}")
                print(f"Inspeção semanal obrigatória: a primeira vence em "
                      f"{veiculo.proxima_inspecao().strftime('%d/%m/%Y')}.\n")

            else:
                # ── Devolver: inspeção final + fatura ──
                aluguel = buscar_aluguel(veiculo.aluguel_id)
                if aluguel is None:
                    print("Não foi possível localizar o registro do aluguel deste veículo.\n")
                    return

                print(f"\nDevolução de {veiculo.cliente}")
                if veiculo.inspecao_atrasada():
                    print("⚠️ A inspeção semanal deste aluguel estava atrasada.")

                realizar_inspecao(veiculo, aluguel, "devolucao")

                aluguel.data_fim = hoje().isoformat()
                aluguel.ativo    = False
                salvar_alugueis()
                exibir_fatura(aluguel)

                veiculo.alugado         = False
                veiculo.cliente         = None
                veiculo.dias_aluguel    = 0
                veiculo.aluguel_id      = None
                veiculo.ultima_inspecao = None
                print("Veículo devolvido com sucesso!")
                if veiculo.danificado:
                    print("⚠️ O veículo está marcado como danificado e ficará "
                          "indisponível até o reparo.")
                print("Multas que chegarem depois são atribuídas pela data da "
                      "infração (opção 17).\n")

        elif opcao == "2":
            if veiculo.danificado:
                veiculo.danificado = False
                print("Status atualizado: SEM DANOS (veículo liberado).")
            elif veiculo.alugado:
                # dano durante o aluguel: o cliente paga e o aluguel continua registrado
                aluguel = buscar_aluguel(veiculo.aluguel_id)
                if aluguel is None:
                    print("Não foi possível localizar o registro do aluguel deste veículo.\n")
                    return
                descricao = ler_texto_obrigatorio("Descrição da avaria: ")
                valor     = ler_dinheiro("Valor a cobrar do cliente (R$): ")
                lancar(aluguel, veiculo.placa, "avaria", descricao, valor)
                veiculo.danificado = True
                print(f"Avaria cobrada de {aluguel.cliente_nome}. Status: DANIFICADO.")
            else:
                veiculo.danificado = True
                print("Status atualizado: DANIFICADO (sem aluguel ativo: sem cobrança de cliente).")
            print()

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
        cpf  = normalizar_cpf(ler_texto_obrigatorio("CPF: "))
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
        novo_cpf = normalizar_cpf(novo_cpf)
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
        if any(a.ativo and a.cliente_cpf == cliente.cpf for a in alugueis):
            print("Este cliente tem um aluguel em andamento. Faça a devolução antes de removê-lo.\n")
            return
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
    cpf = normalizar_cpf(ler_texto_obrigatorio("Digite o CPF: "))
    for c in clientes:
        if c.cpf == cpf:
            c.exibir()
            return
    print("Cliente não encontrado.\n")


# ─────────────────────────────────────────
#  FINANCEIRO
# ─────────────────────────────────────────

def exibir_aluguel_com_cobrancas(aluguel):
    aluguel.exibir()
    extras = cobrancas_do_aluguel(aluguel)
    for l in extras:
        print(f"      + {NOME_TIPO[l.tipo]}: {l.descricao} = R$ {l.valor:.2f}")
    if extras:
        print(f"      Total a cobrar: R$ {total_a_cobrar(aluguel):.2f}")

def soma(tipo, responsavel):
    return round(sum(l.valor for l in lancamentos
                     if l.tipo == tipo and l.responsavel == responsavel), 2)

# função para exibir o histórico de todos os aluguéis realizados, com os totais por responsável
def relatorio_alugueis():
    if not alugueis:
        print("Nenhum aluguel registrado.\n")
        return

    print("\n--- Histórico de Aluguéis ---")
    for i, a in enumerate(alugueis):
        print(f"[{i}]", end=" ")   # exibe o índice do aluguel
        exibir_aluguel_com_cobrancas(a)

    diarias       = round(sum(a.total for a in alugueis), 2)
    avarias       = soma("avaria", "locatario")
    multas_client = soma("multa", "locatario")
    a_receber     = round(diarias + avarias + multas_client, 2)

    manutencao    = soma("manutencao", "locadora")
    multas_loc    = soma("multa", "locadora")
    despesas      = round(manutencao + multas_loc, 2)

    print("\n=== RESUMO FINANCEIRO ===")
    print("A receber dos clientes:")
    print(f"  Diárias:            R$ {diarias:.2f}")
    print(f"  Avarias:            R$ {avarias:.2f}")
    print(f"  Multas repassadas:  R$ {multas_client:.2f}")
    print(f"  Total faturado:     R$ {a_receber:.2f}")
    print("Despesas da locadora:")
    print(f"  Manutenção mecânica:  R$ {manutencao:.2f}")
    print(f"  Multas fora de aluguel: R$ {multas_loc:.2f}")
    print(f"  Total de despesas:    R$ {despesas:.2f}\n")

# função para exibir o histórico de aluguéis de um cliente específico, filtrando pelo CPF e mostrando o total a cobrar
def relatorio_por_cliente():
    cpf       = normalizar_cpf(ler_texto_obrigatorio("CPF do cliente: "))
    resultado = [a for a in alugueis if a.cliente_cpf == cpf]

    if not resultado:
        print("Nenhum aluguel encontrado para esse CPF.\n")
        return

    print(f"\n--- Aluguéis de {resultado[0].cliente_nome} ---")
    total = 0.0
    for a in resultado:
        exibir_aluguel_com_cobrancas(a)
        total += total_a_cobrar(a)       # diárias + avarias + multas deste cliente
    print(f"\nTotal a cobrar do cliente: R$ {total:.2f}\n")


# ─────────────────────────────────────────
#  MENU
# ─────────────────────────────────────────

MENU = [
    ("titulo", "VEÍCULOS"),
    ("1",  "Cadastrar veículo"),
    ("2",  "Listar frota"),
    ("3",  "Alterar status (alugar/devolver)"),
    ("4",  "Editar veículo"),
    ("5",  "Remover veículo"),
    ("6",  "Buscar por placa"),
    ("7",  "Filtrar veículos"),
    ("titulo", "CLIENTES"),
    ("8",  "Cadastrar cliente"),
    ("9",  "Listar clientes"),
    ("10", "Editar cliente"),
    ("11", "Remover cliente"),
    ("12", "Buscar por CPF"),
    ("titulo", "INSPEÇÃO E MULTAS"),
    ("15", "Registrar inspeção semanal"),
    ("16", "Inspeções pendentes"),
    ("17", "Registrar multa de trânsito"),
    ("titulo", "FINANCEIRO"),
    ("13", "Histórico e resumo financeiro"),
    ("14", "Consultar por cliente"),
    ("titulo", None),
    ("0",  "Sair"),
]

def exibir_menu():
    largura = 40
    print("╔" + "═" * largura + "╗")
    print("║" + "LOCADORA — MENU PRINCIPAL".center(largura) + "║")
    for codigo, texto in MENU:
        if codigo == "titulo":
            print("╠" + "═" * largura + "╣")
            if texto:
                print("║" + f"  {texto}".ljust(largura) + "║")
        else:
            print("║" + f"  {codigo.ljust(2)} - {texto}".ljust(largura) + "║")
    print("╚" + "═" * largura + "╝")

ACOES = {
    "1":  cadastrar_veiculo,
    "2":  listar_veiculos,
    "3":  alterar_status,
    "4":  editar_veiculo,
    "5":  remover_veiculo,
    "6":  buscar_por_placa,
    "7":  filtrar_veiculos,
    "8":  cadastrar_cliente,
    "9":  listar_clientes,
    "10": editar_cliente,
    "11": remover_cliente,
    "12": buscar_cliente_por_cpf,
    "13": relatorio_alugueis,
    "14": relatorio_por_cliente,
    "15": registrar_inspecao_semanal,
    "16": inspecoes_pendentes,
    "17": registrar_multa,
}


# ─────────────────────────────────────────
#  INICIALIZAÇÃO
# ─────────────────────────────────────────

def main():
    print("--- Programa para Aluguel de Carros ---\n")

    carregar_frota()
    carregar_clientes()
    carregar_alugueis()
    carregar_lancamentos()
    carregar_inspecoes()
    migrar_dados_antigos()

    while True:
        avisar_inspecoes_atrasadas()
        exibir_menu()
        opcao = input("Escolha: ")

        if opcao == "0":
            print("Dados salvos. Até logo!")
            break
        acao = ACOES.get(opcao)
        if acao:
            acao()
        else:
            print("Opção inválida.\n")


if __name__ == "__main__":
    main()