import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
import uuid
import os

# Lista de fabricantes e modelos
FABRICANTES = [
    ("21", "FIAT"),("59", "VW"),("26", "HYUNDAI"),("56", "TOYOTA"),("25", "HONDA"),
    ("48", "RENAULT"),("29", "JEEP"),("43", "NISSAN"),
    ("5", "A MOTORS"), ("3", "A ROMEO"), ("1", "ACURA"), ("2", "AGRALE"), ("4", "AM GEN"),
    ("6", "AUDI"), ("7", "BMW"), ("8", "BRM"), ("9", "BUGGY"), ("123", "BUGRE"),
    ("14", "C LANDER"), ("10", "CADILLAC"), ("11", "CBT JIPE"), ("136", "CHANA"), ("182", "CHANGAN"),
    ("161", "CHERY"), ("23", "CHEVROLET"), ("12", "CHRYSLER"), ("13", "CITROEN"), ("15", "DAEWOO"),
    ("16", "DAIHATSU"), ("17", "DODGE"), ("147", "EFFA"), ("18", "ENGESA"), ("19", "ENVEMO"),
    ("20", "FERRARI"),  ("149", "FIBRAVAN"), ("22", "FORD"), ("170", "FYBER"),
    ("153", "GREAT WALL"), ("24", "GURGEL"), ("152", "HAFEI"),
    ("27", "ISUZU"), ("177", "JAC"), ("28", "JAGUAR"),  ("154", "JINBEI"),
    ("30", "JPX"), ("31", "KIA"), ("32", "LADA"), ("171", "LAMBORGHINI"), ("33", "LAND ROVER"),
    ("34", "LEXUS"), ("168", "LIFAN"), ("127", "LOBINI"), ("35", "LOTUS"), ("140", "MAHINDRA"),
    ("36", "MASERATI"), ("37", "MATRA"), ("38", "MAZDA"), ("40", "MERCURY"), ("167", "MB"),
    ("156", "MINI"), ("41", "MITSUBISHI"), ("42", "MIURA"), ("44", "PEUGEOT"),
    ("45", "PLYMOUTH"), ("46", "PONTIAC"), ("47", "PORSCHE"), ("185", "RAM"), ("186", "RELY"),
     ("49", "ROVER"), ("50", "SAAB"), ("51", "SATURN"), ("52", "SEAT"),
    ("183", "SHINERAY"), ("157", "SMART"), ("125", "SSANGYONG"), ("54", "SUBARU"), ("55", "SUZUKI"),
    ("165", "TAC"),  ("57", "TROLLER"), ("58", "VOLVO"),
    ("163", "WAKE"), ("120", "WALK")
]

MODELOS = {
    "": [""], "AUDI": ["A3"], "BMW": ["325I", "325iS", "BMW 316I", "F300", "X1"], "CHERY": ["QQ"],
    "CHEVROLET": ["A20", "ADVANCED D", "AGILE", "ASTRA", "AVALANCHE", "BEL AIR", "BLAZER", "BONANZA", "BRASIL", "BRASINCA", "C10", "C14", "C15", "C20", "CALIBRA", "CAMARO", "CAPRICE", "CAPTIVA", "CARAVAN", "CAVALIER", "CELTA", "CHEVELLE", "CHEVETTE", "CHEVY 500", "CHEYENNE", "CLASSIC", "COBALT", "CORSA", "CORVETTE", "CORVETTE G SP", "CRUZE", "D10", "D20", "DE LUXE", "EL CAMINO", "FLEETMASTER", "GRAND BLAZER", "HHR", "IMPALA", "IPANEMA", "JOY", "KADETT", "LUMINA", "MALIBU", "MERIVA", "MONTANA", "MONZA", "OMEGA", "ONIX", "OPALA", "PICKUP", "PRISMA", "S10", "SILVERADO", "SONIC", "SPACE VAN", "SPIN", "SPORT VAN", "SS", "SSR", "SUBURBAN", "SUPREMA", "TAHOE", "TIGRA", "TRACKER", "TRAILBLAZER", "VECTRA", "VERANEIO", "ZAFIRA"],
    "CHRYSLER": ["PT CRUISER"], "CITROEN": ["AIRCROSS", "C3", "C4", "XSARA PCSO"], "DODGE": ["RAM"],
    "FIAT": ["124", "147", "500", "ARGO", "BRAVA", "BRAVO", "CINQUECENTO", "COUPÉ", "CRONOS", "DOBLO", "DUCATO", "DUNA", "ELBA", "FIORINO", "FREEMONT", "GRAND SIENA", "IDEA", "LINEA", "MAREA", "MOBI", "OGGI", "PALIO", "PANORAMA", "PREMIO", "PULSE", "PUNTO", "SIENA", "STILO", "STRADA", "TEMPRA", "TIPO", "TORO", "UNO"],
    "FORD": ["A", "BELINA", "CLUB WAGON", "CORCEL", "CORCEL II", "COURIER", "CUSTOM", "DEL REY", "ECOSPORT", "EDGE", "ESCAPE", "ESCORT", "EXPLORER", "F-1", "F-100", "F-1000", "F-150", "F-250", "F-350", "F-4000", "F-75", "FAIRLANE", "FIESTA", "FLEX", "FOCUS", "FURGLAINE", "FUSION", "GALAXIE", "GT", "IBIZA", "JEEP", "KA", "KA +", "LANDAU", "MAVERICK", "MONDEO", "MUSTANG", "MUSTANG V6", "PAMPA", "PHAETON", "RANGER", "ROYALE", "RURAL", "SUPER DLUX", "TAURUS", "THUNDERBIRD", "TRANSIT", "TUDOR", "VERONA", "VERSAILLES"],
    "HONDA": ["ACCORD", "BIZ", "CB", "CB 500", "CB 600", "CB 650", "CBR", "CG", "CITY", "CIVIC", "CRV", "FIT", "HR-V", "LEGEND", "NXR", "ODYSSEY", "PCX", "PILOT", "PRELUDE", "XRE"],
    "HYUNDAI": ["ACCENT", "ATOS", "AZERA", "CRETA", "ELANTRA", "EQUUS", "GALLOPER", "GENESIS", "GRAND STA FÉ", "H1 STAREX", "H100", "HB20", "HB20S", "HB20X", "HR", "I30", "I30 CW", "IX35", "SANTA FÉ", "SONATA", "TERRACAN", "TIBURON", "TUCSON", "VELOSTER", "VERA CRUZ"],
    "IVECO": ["DAILY"], "JEEP": ["CHEROKEE", "COMPASS", "GRAND CHEROKEE", "RENEGADE", "WRANGLER"],
    "KIA": ["BESTA", "BONGO", "CADENZA", "CARENS", "CARNIVAL", "CERATO", "CLARUS", "MAGENTIS", "MOHAVE", "OPIRUS", "OPTIMA", "PICANTO", "QUORIS", "SHUMA", "SORENTO", "SOUL", "SPORTAGE"],
    "LAND ROVER": ["DEFENDER", "DISCOVERY", "DISCOVERY 2", "DISCOVERY 3", "DISCOVERY 4", "FREELANDER", "FREELANDER 2", "RANGE ROVER", "RANGE ROVER SPORT", "RANGE ROVER VOGUE", "RANGER ROVER EVOQUE", "RANGER ROVER VELAR"],
    "MERC BENZ": ["L1620"], "MINI": ["COOPER"], "MITSUBISHI": ["L200", "OUTLANDER", "PAJERO SPORT", "PAJERO TR4"], "MUUV": ["BEACH"],
    "NISSAN": ["240SX", "300 ZX", "350Z", "370Z", "ALTIMA", "ARMADA", "FRONTIER", "GRAND LIVINA", "GT-R", "JUKE", "KICKS", "LIVINA", "MARCH", "MAXIMA", "MURANO", "PATHFINDER", "QUEST", "SENTRA", "TERRANO", "TIIDA", "VERSA", "X-TRAIL", "XTERRA"],
    "PEUGEOT": ["106", "2008", "205", "206", "207", "208", "3008", "306", "307", "308", "405", "406", "407", "408", "504", "508", "605", "607", "BOXER", "HOGGAR", "PARTNER", "RCZ"],
    "RENAULT": ["19", "CAPTUR", "CLIO", "DAUPHINE", "DUSTER", "DUSTER OROCH", "EXPRESS", "FLUENCE", "GORDINI", "GRAND SCENIC", "KANGOO", "KWID", "LAGUNA", "LOGAN", "MASTER", "MEGANE", "SANDERO", "SCENIC", "SYMBOL", "TRAFIC", "TWINGO"],
    "SUZUKI": ["BALENO", "GRAND VITARA", "IGNIS", "JIMNY", "S-CROSS", "SAMURAI", "SIDEKICK", "SWIFT", "SX4", "VITARA"],
    "TOYOTA": ["4RUNNER", "AVALON", "BANDEIRANTE", "CAMRY", "CELICA", "COROLLA", "CORONA", "ETIOS", "ETIOS CROSS", "FIELDER", "FJ CRUISER", "HIGHLANDER", "HILUX", "HILUX SW4", "LAND C PRADO", "LEXUS", "MR-2", "PASEO", "PREVIA", "PRIUS", "RAV4", "SIENNA", "TUNDRA", "VENZA"],
    "VEICULOS ESPECIAS": ["CONJUNTO PESCA"],
    "VOLVO": ["460", "850", "960", "C30", "C70", "S40", "S60", "S70", "S80", "V40", "V50", "V60", "V70", "XC60", "XC70", "XC90"],
    "VW": ["1300", "1600", "AMAROK", "APOLLO", "BORA", "BRASILIA", "BUGGY", "CARAVELLE", "CROSS UP", "CROSSFOX", "EOS", "EUROVAN", "FOX", "FUSCA", "GOL", "GOLF", "JETTA", "KARMANN-G", "KOMBI", "LOGUS", "NEW BEETLE", "NIVUS", "PARATI", "PASSAT", "PASSAT VAR", "POINTER", "POLO", "POLO SEDAN", "QUANTUM", "SANTANA", "SAVEIRO", "SCIROCCO", "SP2", "SPACE CROSS", "SPACEFOX", "T-CROSS", "TIGUAN", "TL", "TOUAREG", "UP", "VAN", "VARIANT", "VARIANT II", "VIRTUS", "VOYAGE"],
    "YAMAHA": ["XTZ250"]
}
CORS = [
    ("8", "AMARELA"), ("2", "AZUL"), ("5", "AZUL MT"), ("19", "BEGE"),
    ("1", "BRANCA"), ("18", "BRANCO PL"), ("16", "CINZA"), ("7", "CINZA MT"), ("12", "DOURADA"),
    ("17", "LARANJA"), ("13", "LILÁS"), ("10", "MARRON"), ("9", "PRATA"), ("4", "PRETA"),
    ("11", "PRETA MT"), ("21", "ROSA"), ("3", "ROXO"), ("22", "VERDE"),
    ("23", "VERDE MT"), ("6", "VERMELHA"), ("15", "VERMELHO MT"), ("20", "VINHO")
]

CATEGORIA = [
    ("26", "Hatch"), ("16", "Sedan"), ("20", "SUV"), ("14", "Picape"),
    ("14", "Perua"), ("11", "Minivan"), ("13", "Off-Road"), ("24", "Van"),
    ("1", "Caminhão"), ("2", "Outros")
]

def pesquisar_observacao(nome_cliente):
    try:
        with open('clientes.json', 'r') as file:
            clientes_data = json.load(file)
            for cliente in clientes_data:
                cliente_nome_normalizado = cliente['nome'].strip().lower()
                if nome_cliente.strip().lower() == cliente_nome_normalizado:
                    return cliente.get('observacao', '').strip()
    except FileNotFoundError:
        return 'Arquivo de clientes não encontrado'
    except json.JSONDecodeError:
        return 'Erro ao ler o arquivo JSON'
    return None

def pesquisar_telefone(nome):
    try:
        with open('clientes.json', 'r') as file:
            clientes_data = json.load(file)
            nome_normalizado = nome.strip().lower()
            for cliente in clientes_data:
                cliente_nome_normalizado = cliente['nome'].strip().lower()
                if nome_normalizado == cliente_nome_normalizado:
                    return cliente.get('telefones', 'Telefone não encontrado')
    except FileNotFoundError:
        return 'Arquivo de clientes não encontrado'

def carregar_clientes():
    try:
        with open('clientes.json', 'r') as file:
            clientes_data = json.load(file)
            nomes_clientes = sorted([cliente['nome'] for cliente in clientes_data])
            return [''] + nomes_clientes
    except FileNotFoundError:
        return []

def carregar_contador_id():
    if os.path.exists('contador.json'):
        with open('contador.json', 'r') as file:
            return json.load(file)["contador_id"]
    else:
        return 0

def salvar_contador_id(contador_id):
    with open('contador.json', 'w') as file:
        json.dump({"contador_id": contador_id}, file)

contador_id = carregar_contador_id()

class Proposta:
    def __init__(self, id, fabricante, modelo, categoria, ano_min, ano_max, cor, preco_min, preco_max, tipo, data_inclusao, pessoa_empresa):
        self.id = id
        self.fabricante = fabricante
        self.modelo = modelo
        self.categoria = categoria
        self.ano_min = ano_min
        self.ano_max = ano_max
        self.cor = cor
        self.preco_min = preco_min
        self.preco_max = preco_max
        self.tipo = tipo
        self.data_inclusao = data_inclusao
        self.pessoa_empresa = pessoa_empresa

    def to_dict(self):
        return {"id": self.id, "fabricante": self.fabricante, "modelo": self.modelo, "categoria": self.categoria, "ano_min": self.ano_min, "ano_max": self.ano_max, "cor": self.cor, "preco_min": self.preco_min, "preco_max": self.preco_max, "tipo": self.tipo, "data_inclusao": self.data_inclusao, "pessoa_empresa": self.pessoa_empresa}

    @classmethod
    def from_dict(cls, data):
        return cls(data['id'], data['fabricante'], data['modelo'], data['categoria'], data['ano_min'], data['ano_max'], data['cor'], data['preco_min'], data['preco_max'], data['tipo'], data['data_inclusao'], data['pessoa_empresa'])

def carregar_propostas():
    try:
        with open('propostas.json', 'r') as file:
            propostas_data = json.load(file)
            return [Proposta.from_dict(item) for item in propostas_data]
    except FileNotFoundError:
        return []

def salvar_propostas(propostas):
    with open('propostas.json', 'w') as file:
        json.dump([p.to_dict() for p in propostas], file, indent=4)

def adicionar_proposta():
    global contador_id
    fabricante = fabricante_var.get()
    modelo = modelo_var.get()
    categoria = categoria_var.get()
    ano_min = ano_min_var.get()
    ano_max = ano_max_var.get()
    cor = cor_var.get()
    preco_min = preco_min_var.get()
    preco_max = preco_max_var.get()
    tipo = tipo_var.get()
    pessoa_empresa = pessoa_empresa_var.get()
    data_inclusao = datetime.now().strftime("%d-%m-%Y")

    if not pessoa_empresa:
        messagebox.showwarning("Atenção", "Por favor, preencha o campo 'Pessoa/Empresa'.")
        return
    clientes = carregar_clientes()
    if pessoa_empresa not in clientes:
        messagebox.showwarning("Atenção", "Por favor, insira um nome válido que já exista no cadastro de clientes.")
        return
    if tipo not in ["Compra", "Venda"]:
        messagebox.showwarning("Atenção", "Por favor, selecione um tipo válido: 'Compra' ou 'Venda'.")
        return

    nova_proposta = Proposta(
        id=str(contador_id),
        fabricante=fabricante if fabricante != "Escolha..." else "",
        modelo=modelo if modelo != "Escolha..." else "",
        categoria=categoria if categoria != "Escolha..." else "",
        ano_min=ano_min,
        ano_max=ano_max,
        cor=cor if cor != "Escolha..." else "",
        preco_min=preco_min,
        preco_max=preco_max,
        tipo=tipo,
        data_inclusao=data_inclusao,
        pessoa_empresa=pessoa_empresa,
    )

    propostas = carregar_propostas()
    propostas.append(nova_proposta)
    salvar_propostas(propostas)
    messagebox.showinfo("Proposta Recebida", f"Sua proposta (ID: {nova_proposta.id}) foi recebida com sucesso!")

    # Executa a pesquisa automática com o nome vazio para achar todos os "matches"
    criterios_pesquisa = Proposta.from_dict(nova_proposta.to_dict())
    criterios_pesquisa.pessoa_empresa = ""
    mostrar_propostas_relevantes_pesquisa(criterios_pesquisa)

    contador_id += 1
    salvar_contador_id(contador_id)

def pesquisar_proposta():
    # Esta função agora apenas monta os critérios e chama a busca, sem salvar nada.
    criterios_de_busca = Proposta(
        id="temp_search",
        fabricante=fabricante_var.get() if fabricante_var.get() != "Escolha..." else "",
        modelo=modelo_var.get() if modelo_var.get() != "Escolha..." else "",
        categoria=categoria_var.get() if categoria_var.get() != "Escolha..." else "",
        ano_min=ano_min_var.get(),
        ano_max=ano_max_var.get(),
        cor=cor_var.get() if cor_var.get() != "Escolha..." else "",
        preco_min=preco_min_var.get(),
        preco_max=preco_max_var.get(),
        tipo=tipo_var.get(),
        data_inclusao="",
        pessoa_empresa=pessoa_empresa_var.get(),
    )
    mostrar_propostas_relevantes_pesquisa(criterios_de_busca)

def mostrar_propostas_relevantes_pesquisa(criterios_de_busca):
    propostas = carregar_propostas()
    relevantes = []
    
    if criterios_de_busca.tipo == "Compra": tipos_compativeis = ["Venda"]
    elif criterios_de_busca.tipo == "Venda": tipos_compativeis = ["Compra"]
    else: tipos_compativeis = ["Compra", "Venda"]

    for proposta in propostas:
        if proposta.tipo in tipos_compativeis:
            if criterios_de_busca.pessoa_empresa == "" or criterios_de_busca.pessoa_empresa == proposta.pessoa_empresa:
                fabricante_compat = criterios_de_busca.fabricante == "" or criterios_de_busca.fabricante == proposta.fabricante
                modelo_compat = criterios_de_busca.modelo == "" or criterios_de_busca.modelo == proposta.modelo
                categoria_compat = criterios_de_busca.categoria == "" or criterios_de_busca.categoria == proposta.categoria
                cor_compat = criterios_de_busca.cor == "" or criterios_de_busca.cor == proposta.cor

                proposta_ano_min = int(proposta.ano_min) if proposta.ano_min else 0
                proposta_ano_max = int(proposta.ano_max) if proposta.ano_max else 9999
                criterio_ano_min = int(criterios_de_busca.ano_min) if criterios_de_busca.ano_min else 0
                criterio_ano_max = int(criterios_de_busca.ano_max) if criterios_de_busca.ano_max else 9999
                ano_compat = proposta_ano_max >= criterio_ano_min and proposta_ano_min <= criterio_ano_max

                proposta_preco_min = float(proposta.preco_min.replace('.', '')) if proposta.preco_min else 0
                proposta_preco_max = float(proposta.preco_max.replace('.', '')) if proposta.preco_max else float('inf')
                criterio_preco_min = float(criterios_de_busca.preco_min.replace('.', '')) if criterios_de_busca.preco_min else 0
                criterio_preco_max = float(criterios_de_busca.preco_max.replace('.', '')) if criterios_de_busca.preco_max else float('inf')
                preco_compat = proposta_preco_max >= criterio_preco_min and proposta_preco_min <= criterio_preco_max

                if fabricante_compat and modelo_compat and categoria_compat and cor_compat and ano_compat and preco_compat:
                    relevantes.append(proposta)

    relevantes.reverse()
    if relevantes:
        mensagem = "Propostas relacionadas encontradas:\n\n"
        for p in relevantes:
            mensagem = formatar_dados(p, mensagem)
        atualizar_texto(mensagem)
    else:
        atualizar_texto("Nenhuma proposta compatível encontrada.")

def limpar_campos():
    fabricante_var.set("Escolha...")
    modelo_var.set("Escolha...")
    categoria_var.set("Escolha...")
    ano_min_var.set("")
    ano_max_var.set("")
    cor_var.set("Escolha...")
    preco_min_var.set("")
    preco_max_var.set("")
    tipo_var.set("")
    pessoa_empresa_var.set("")

def atualizar_modelos(*args):
    fabricante = fabricante_var.get()
    modelos = MODELOS.get(fabricante, ["Escolha..."])
    modelo_combobox['values'] = modelos
    modelo_combobox.set("Escolha...")

def ocultar_proposta():
    numero_ocultar = ocultar_var.get()
    if not numero_ocultar:
        mostrar_mensagem("Por favor, insira o número da proposta a ser ocultada.")
        return
    propostas = carregar_propostas()
    propostas_filtradas = [p for p in propostas if p.id != numero_ocultar]
    if len(propostas) == len(propostas_filtradas):
        mostrar_mensagem("Nenhuma proposta encontrada com esse número.")
    else:
        salvar_propostas(propostas_filtradas)
        mostrar_mensagem(f"Proposta {numero_ocultar} ocultada com sucesso!")

def formatar_dados(p, mensagem):
    mensagem += f"{p.id}||{p.data_inclusao} ||"
    if p.tipo: mensagem += f" {p.tipo} "
    if p.fabricante: mensagem += f"{p.fabricante} "
    if p.categoria: mensagem += f"{p.categoria} "
    if p.modelo: mensagem += f"{p.modelo} "
    if p.ano_min or p.ano_max: mensagem += f"{p.ano_min}-{p.ano_max} "
    if p.pessoa_empresa: mensagem += f"{p.pessoa_empresa} "
    telefone = pesquisar_telefone(p.pessoa_empresa)
    if telefone: mensagem += f"{telefone} "
    obser = pesquisar_observacao(p.pessoa_empresa)
    if obser: mensagem += f"{obser} "
    mensagem += f"\n{'--' * 40}\n"
    return mensagem

def atualizar_texto(mensagem):
    resultado_texto.delete(1.0, tk.END)
    resultado_texto.insert(tk.END, mensagem)

def mostrar_mensagem(mensagem):
    resultado_texto.delete(1.0, tk.END)
    resultado_texto.insert(tk.END, mensagem)

def criar_interface():
    global resultado_texto, ocultar_var, preco_min_var, preco_max_var
    global pessoa_empresa_var, tipo_var, categoria_var, modelo_var, fabricante_var, ano_min_var, ano_max_var, cor_var, modelo_combobox

    root = tk.Tk()
    root.title("Cadastro de Propostas")

    tk.Label(root, text="Pessoa/Empresa").grid(row=0, column=0, padx=5, pady=2, sticky='w')
    pessoa_empresa_var = tk.StringVar()
    clientes = carregar_clientes()
    pessoa_empresa_combobox = ttk.Combobox(root, textvariable=pessoa_empresa_var, values=clientes)
    pessoa_empresa_combobox.grid(row=0, column=1, padx=5, pady=2, sticky='we')

    def atualizar_sugestoes(event):
        texto_digitado = pessoa_empresa_var.get()
        sugestoes = [cliente for cliente in carregar_clientes() if texto_digitado.lower() in cliente.lower()]
        pessoa_empresa_combobox['values'] = sugestoes
        pessoa_empresa_combobox.set(texto_digitado)
    pessoa_empresa_combobox.bind("<KeyRelease>", atualizar_sugestoes)

    tk.Label(root, text="Tipo").grid(row=1, column=0, padx=5, pady=2, sticky='w')
    tipo_var = tk.StringVar()
    ttk.Combobox(root, textvariable=tipo_var, values=["", "Compra", "Venda"]).grid(row=1, column=1, padx=5, pady=2, sticky='we')

    tk.Label(root, text="Categoria").grid(row=2, column=0, padx=5, pady=2, sticky='w')
    categoria_var = tk.StringVar(value="")
    ttk.Combobox(root, textvariable=categoria_var, values=[""] + [c[1] for c in CATEGORIA]).grid(row=2, column=1, padx=5, pady=2, sticky='we')

    tk.Label(root, text="Fabricante").grid(row=3, column=0, padx=5, pady=2, sticky='w')
    fabricante_var = tk.StringVar(value="")
    fabricante_combobox = ttk.Combobox(root, textvariable=fabricante_var, values=[""] + [f[1] for f in FABRICANTES])
    fabricante_combobox.grid(row=3, column=1, padx=5, pady=2, sticky='we')
    fabricante_combobox.bind("<<ComboboxSelected>>", atualizar_modelos)

    tk.Label(root, text="Modelo").grid(row=4, column=0, padx=5, pady=2, sticky='w')
    modelo_var = tk.StringVar(value="")
    modelo_combobox = ttk.Combobox(root, textvariable=modelo_var, values=[""])
    modelo_combobox.grid(row=4, column=1, padx=5, pady=2, sticky='we')

    tk.Label(root, text="Ano Min").grid(row=5, column=0, padx=5, pady=2, sticky='w')
    ano_min_var = tk.StringVar()
    tk.Entry(root, textvariable=ano_min_var).grid(row=5, column=1, padx=5, pady=2, sticky='we')

    tk.Label(root, text="Ano Max").grid(row=6, column=0, padx=5, pady=2, sticky='w')
    ano_max_var = tk.StringVar()
    tk.Entry(root, textvariable=ano_max_var).grid(row=6, column=1, padx=5, pady=2, sticky='we')

    tk.Label(root, text="Cor").grid(row=7, column=0, padx=5, pady=2, sticky='w')
    cor_var = tk.StringVar(value="")
    ttk.Combobox(root, textvariable=cor_var, values=[""] + [c[1] for c in CORS]).grid(row=7, column=1, padx=5, pady=2, sticky='we')

    tk.Label(root, text="Preço Min").grid(row=8, column=0, padx=5, pady=2, sticky='w')
    preco_min_var = tk.StringVar()
    tk.Entry(root, textvariable=preco_min_var).grid(row=8, column=1, padx=5, pady=2, sticky='we')

    tk.Label(root, text="Preço Max").grid(row=9, column=0, padx=5, pady=2, sticky='w')
    preco_max_var = tk.StringVar()
    tk.Entry(root, textvariable=preco_max_var).grid(row=9, column=1, padx=5, pady=2, sticky='we')
    
    # Frame para os botões principais
    botoes_frame = tk.Frame(root)
    botoes_frame.grid(row=10, column=0, columnspan=2, pady=10)
    tk.Button(botoes_frame, text="Pesquisar", command=pesquisar_proposta).pack(side=tk.LEFT, padx=10)
    tk.Button(botoes_frame, text="Enviar Proposta", command=adicionar_proposta).pack(side=tk.LEFT, padx=10)

    # Frame para ocultar proposta
    ocultar_frame = tk.Frame(root)
    ocultar_frame.grid(row=11, column=0, columnspan=2, pady=5)
    tk.Button(ocultar_frame, text="Ocultar Proposta por ID:", command=ocultar_proposta).pack(side=tk.LEFT, padx=5)
    ocultar_var = tk.StringVar()
    tk.Entry(ocultar_frame, textvariable=ocultar_var, width=10).pack(side=tk.LEFT)

    resultado_texto = tk.Text(root, height=20, width=100)
    resultado_texto.grid(row=12, column=0, columnspan=2, padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    criar_interface()