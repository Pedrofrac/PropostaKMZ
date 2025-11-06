import json
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

# Lista para armazenar os clientes
clientes = []

class Cliente:
    def __init__(self, id, nome, cpf, rg, nascimento, telefones, cep, complemento, observacao, email=""):
        self.id = id
        self.nome = nome
        self.cpf = cpf
        self.rg = rg
        self.nascimento = nascimento
        self.telefones = telefones
        self.cep = cep
        self.complemento = complemento
        self.observacao = observacao
        self.email = email  # Novo campo de e-mail

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "cpf": self.cpf,
            "rg": self.rg,
            "nascimento": self.nascimento,
            "telefones": self.telefones,
            "cep": self.cep,
            "complemento": self.complemento,
            "observacao": self.observacao,
            "email": self.email,  # Incluir o e-mail no dicionário
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data['id'],
            data['nome'],
            data['cpf'],
            data['rg'],
            data['nascimento'],
            data['telefones'],
            data['cep'],
            data['complemento'],
            data['observacao'],
            data.get('email', ""),  # Obter o e-mail ou definir como vazio caso não exista
        )

def carregar_clientes():
    try:
        with open('clientes.json', 'r') as file:
            clientes_data = json.load(file)
            return [Cliente.from_dict(item) for item in clientes_data]
    except FileNotFoundError:
        return []

def salvar_clientes(clientes):
    with open('clientes.json', 'w') as file:
        json.dump([c.to_dict() for c in clientes], file, indent=4)

def gerar_id_unico():
    return len(clientes) + 1  # Exemplo simples de geração de ID

def validar_cep(cep):
    # Remove qualquer formatação
    cep = cep.replace("-", "").strip()
    # O CEP deve ter 8 dígitos
    return cep == "" or (len(cep) == 8 and cep.isdigit())

def adicionar_cliente(nome, cpf, rg, nascimento, telefones, cep, complemento, observacao, email):
    # Verifica se o nome já existe
    if verificar_existencia_nome(nome):
        messagebox.showwarning("Aviso", "Esse Nome já está cadastrado! Edite ou faça outro cadastro")
        return

    # Se CPF for fornecido, validá-lo, caso contrário, permitimos CPF vazio.
    if cpf and not validar_cpf(cpf):
        atualizar_texto("CPF inválido! O CPF deve conter 11 ou 14 caracteres (formatado).")
        return

    if cpf and verificar_existencia_cliente(cpf):
        messagebox.showwarning("Aviso", "Esse CPF/CNPJ já está cadastrado! Edite ou faça outro cadastro")
        return

    novo_cliente = Cliente(
        id=gerar_id_unico(),
        nome=nome,
        cpf=cpf,
        rg=rg,
        nascimento=nascimento,
        telefones=telefones,
        cep=cep,
        complemento=complemento,
        observacao=observacao,
        email=email  # Passa o e-mail para o novo cliente
    )
    clientes.append(novo_cliente)
    salvar_clientes(clientes)

def verificar_existencia_nome(nome):
    for cliente in clientes:
        if cliente.nome.lower() == nome.lower():  # Ignora diferença entre maiúsculas e minúsculas
            return True
    return False

def mostrar_clientes_semelhantes():
    pesquisa_nome = pesquisa_nome_var.get().strip().lower()
    semelhantes = [c for c in clientes if pesquisa_nome in c.nome.lower()]

    if semelhantes:
        if len(semelhantes) == 1:
            global cliente_atual  # Define a variável global para o cliente que será editado
            cliente_atual = semelhantes[0]
            
            # Preenche os campos com os dados do cliente encontrado
            nome_var.set(cliente_atual.nome)
            cpf_var.set(cliente_atual.cpf)
            rg_var.set(cliente_atual.rg)
            nascimento_var.set(cliente_atual.nascimento)
            telefones_var.set(cliente_atual.telefones)
            cep_var.set(cliente_atual.cep)
            complemento_var.set(cliente_atual.complemento)
            observacao_text.delete("1.0", tk.END)  # Limpa o campo de texto
            observacao_text.insert(tk.END, cliente_atual.observacao)  # Insere a observação
            email_var.set(cliente_atual.email)  # Exibe o e-mail no campo de entrada
            atualizar_texto("Cliente encontrado e dados preenchidos nos campos.")
            
            # Habilita o botão de edição
            botao_editar.config(state=tk.NORMAL)
            botao_excluir.config(state=tk.NORMAL)
        else:
            mensagem = "Clientes encontrados:\n\n"
            for cliente in semelhantes:
                mensagem += f"\nNome: {cliente.nome} || "
                mensagem += f"CPF: {cliente.cpf} || " if cliente.cpf else ""
                mensagem += f"RG: {cliente.rg} || " if cliente.rg else ""
                mensagem += f"Nascimento: {cliente.nascimento}" if cliente.nascimento else ""
                mensagem += f"\nTelefone: {cliente.telefones}\n" if cliente.telefones else ""
                mensagem += f"Email: {cliente.email}\n" if cliente.email else ""  # Inclui o e-mail
                mensagem += f"\nCEP: {cliente.cep} || " if cliente.cep else ""
                mensagem += f"Complemento: {cliente.complemento}\n" if cliente.complemento else ""
                mensagem += f"\nObservação: {cliente.observacao}" if cliente.observacao else ""
                mensagem += "\n------------------------\n\n"  # Separar os clientes com uma linha em branco
            atualizar_texto(mensagem)
            botao_editar.config(state=tk.DISABLED)
            botao_excluir.config(state=tk.DISABLED)

    else:
        atualizar_texto("Nenhum cliente encontrado com esse nome.")
        botao_editar.config(state=tk.DISABLED)
        botao_excluir.config(state=tk.DISABLED)

def atualizar_texto(mensagem):
    resultado_texto.delete(1.0, tk.END)
    resultado_texto.insert(tk.END, mensagem)

def cadastrar_cliente():
    nome = nome_var.get()
    cpf = cpf_var.get()

    # Validação do nome
    if not validar_nome(nome):
        atualizar_texto("O nome não pode estar em branco.")
        return
    
    # Validação do CPF
    if cpf and not validar_cpf(cpf):
        atualizar_texto("CPF inválido! O CPF deve conter 11 ou 14 caracteres (formatado).")
        return
    
    rg = rg_var.get()
    nascimento = nascimento_var.get()
    telefones = telefones_var.get()
    cep = cep_var.get()
    
    # Validação do CEP
    if not validar_cep(cep):
        atualizar_texto("CEP inválido! O CEP deve estar no formato 00000-000 ou vazio.")
        return
    
    complemento = complemento_var.get().strip()
    
    # Verifica se o complemento é obrigatório
    if cep and not complemento:
        atualizar_texto("O complemento é obrigatório quando o CEP é preenchido.")
        return
    
    observacao = observacao_text.get("1.0", tk.END).strip()  # Pega o texto do widget Text
    email = email_var.get().strip()  # Pega o e-mail inserido

    adicionar_cliente(nome, cpf, rg, nascimento, telefones, cep, complemento, observacao, email)
    atualizar_texto("Cliente cadastrado com sucesso!")

def verificar_existencia_cliente(cpf):
    for cliente in clientes:
        if cliente.cpf == cpf:
            return True
    return False

def formatar_cep(event):
    # Obtém o valor do campo de CEP sem formatação
    cep = cep_var.get().replace(".", "").replace("-", "").replace(" ", "")
    
    # Limita a entrada a no máximo 8 dígitos
    if len(cep) > 8:
        cep = cep[:8]
    
    # Aplica a formatação no formato XX.XXX-XXX
    if len(cep) >= 6:
        cep = f"{cep[:2]}.{cep[2:5]}-{cep[5:]}"
    elif len(cep) >= 3:
        cep = f"{cep[:2]}.{cep[2:]}"
    
    # Atualiza o campo de entrada com o CEP formatado
    cep_var.set(cep)
    
    # Move o cursor para a posição correta
    event.widget.icursor(len(cep))

def formatar_documento(event):
    # Obtém o valor do campo de CPF ou CNPJ
    documento = cpf_var.get().replace(".", "").replace("-", "").replace("/", "").replace(" ", "")

    # Limita a entrada a no máximo 14 dígitos
    if len(documento) > 14:
        documento = documento[:14]

    # Define a função de formatação para CPF
    def formata_cpf(cpf):
        if len(cpf) == 11:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        elif len(cpf) >= 7:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:]}"
        elif len(cpf) >= 4:
            return f"{cpf[:3]}.{cpf[3:]}"
        return cpf

    # Define a função de formatação para CNPJ
    def formata_cnpj(cnpj):
        if len(cnpj) == 14:
            return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
        elif len(cnpj) >= 12:
            return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:]}"
        elif len(cnpj) >= 9:
            return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:]}"
        return cnpj

    # Aplica a formatação apropriada
    if len(documento) <= 11:
        formato = formata_cpf(documento)
    else:
        formato = formata_cnpj(documento)

    # Atualiza o campo de entrada com a string formatada
    cpf_var.set(formato)

    # Move o cursor para a posição correta
    event.widget.icursor(len(formato))

def validar_cpf(cpf):
    # Remove qualquer formatação como ".", "-", "/", etc.
    documento = cpf.replace(".", "").replace("-", "").replace("/", "").replace(" ", "")
    
    # CPF tem 11 dígitos e CNPJ tem 14 dígitos
    if len(documento) == 11:
        return documento.isdigit()  # Verifica se é numérico e tem o comprimento correto de CPF
    elif len(documento) == 14:
        return documento.isdigit()  # Verifica se é numérico e tem o comprimento correto de CNPJ
    else:
        return False

def validar_nome(nome):
    return bool(nome.strip())

def editar_cliente():
    global cliente_atual  # Acessa o cliente atual
    if not cliente_atual:
        atualizar_texto("Nenhum cliente selecionado para edição.")
        return

    # Pegue os valores dos campos editados
    nome = nome_var.get()
    cpf = cpf_var.get()
    rg = rg_var.get()
    nascimento = nascimento_var.get()
    telefones = telefones_var.get()
    cep = cep_var.get()
    complemento = complemento_var.get()
    observacao = observacao_text.get("1.0", tk.END).strip()

    # Salva o nome e CPF antigos antes de atualizar
    nome_antigo = cliente_atual.nome
    cpf_antigo = cliente_atual.cpf

    # Verifica se o CPF foi alterado e se já existe outro cliente com o novo CPF, excluindo o cliente atual da verificação
    if cpf != cpf_antigo and cpf and verificar_existencia_cliente(cpf):
        atualizar_texto("Outro cliente com este CPF já existe!")
        return

    # Atualiza os dados do cliente
    cliente_atual.nome = nome
    cliente_atual.cpf = cpf
    cliente_atual.rg = rg
    cliente_atual.nascimento = nascimento
    cliente_atual.telefones = telefones
    cliente_atual.cep = cep
    cliente_atual.complemento = complemento
    cliente_atual.observacao = observacao

    # Atualiza as propostas associadas ao cliente (caso o nome tenha mudado)
    if nome != nome_antigo:
        try:
            # Carrega o arquivo de propostas
            with open("propostas.json", "r", encoding="utf-8") as f:
                propostas = json.load(f)

            # Atualiza as propostas que possuem o nome antigo
            for proposta in propostas:
                if proposta.get("pessoa_empresa") == nome_antigo:
                    proposta["pessoa_empresa"] = nome

            # Salva as propostas atualizadas de volta no arquivo
            with open("propostas.json", "w", encoding="utf-8") as f:
                json.dump(propostas, f, indent=4, ensure_ascii=False)

        except FileNotFoundError:
            atualizar_texto("Arquivo propostas.json não encontrado.")
        except json.JSONDecodeError:
            atualizar_texto("Erro ao ler o arquivo propostas.json.")

    # Agora, vamos atualizar o arquivo de clientes (clientes.json)
    try:
        # Carrega os clientes do arquivo
        with open("clientes.json", "r+", encoding="utf-8") as f:
            clientes = json.load(f)

            # Atualiza os dados do cliente na lista de clientes
            for i, cliente in enumerate(clientes):
                if cliente["id"] == cliente_atual.id:
                    clientes[i] = cliente_atual.__dict__  # Substitui o cliente com os dados atualizados
                    break

            # Move o ponteiro para o início do arquivo e sobrescreve o conteúdo
            f.seek(0)
            f.truncate()  # Limpa o arquivo antes de escrever
            json.dump(clientes, f, indent=4, ensure_ascii=False)

        atualizar_texto("Dados do cliente atualizados com sucesso!")
        
    except FileNotFoundError:
        atualizar_texto("Arquivo clientes.json não encontrado.")
    except json.JSONDecodeError:
        atualizar_texto("Erro ao ler o arquivo clientes.json.")

    # Desabilita os botões de edição e exclusão após a edição
    botao_editar.config(state=tk.DISABLED)
    botao_excluir.config(state=tk.DISABLED)  # Desabilita o botão de excluir também


def excluir_cliente():
    global cliente_atual  # Acessa o cliente atual
    if cliente_atual:
        # Remove o cliente da lista
        clientes.remove(cliente_atual)
        
        # Salva as alterações no arquivo clientes
        salvar_clientes(clientes)
        
        # Tenta excluir o cliente de propostas.json, se existir
        try:
            with open("propostas.json", "r", encoding="utf-8") as file:
                propostas = json.load(file)
            
            # Acessa o atributo 'nome' de cliente_atual (supondo que seja um atributo da classe)
            nome_cliente = cliente_atual.nome  # Acessando o atributo 'nome' diretamente
            
            # Filtra as propostas para remover o cliente com o nome correspondente
            propostas = [proposta for proposta in propostas if proposta['pessoa_empresa'] != nome_cliente]
            
            # Regrava as alterações no arquivo propostas.json
            with open("propostas.json", "w", encoding="utf-8") as file:
                json.dump(propostas, file, indent=4, ensure_ascii=False)
        
        except FileNotFoundError:
            # Caso o arquivo propostas.json não exista, apenas ignora
            print("Arquivo propostas.json não encontrado.")
        except json.JSONDecodeError:
            # Caso haja um erro na leitura do JSON
            print("Erro ao ler o arquivo propostas.json.")
        
        # Atualiza a interface
        atualizar_texto("Cliente excluído com sucesso!")
        
        # Limpa os campos de entrada
        nome_var.set("")
        cpf_var.set("")
        rg_var.set("")
        nascimento_var.set("")
        telefones_var.set("")
        cep_var.set("")
        complemento_var.set("")
        observacao_text.delete("1.0", tk.END)  # Limpa o campo de observação
        
        # Desabilita os botões de edição e exclusão
        botao_editar.config(state=tk.DISABLED)
        botao_excluir.config(state=tk.DISABLED)

def criar_interface():
    global resultado_texto, pesquisa_nome_var
    global nome_var, cpf_var, rg_var, nascimento_var, telefones_var, cep_var, complemento_var, observacao_var, observacao_text, email_var  # Adicionar email_var aqui
    
    root = tk.Tk()
    root.title("Cadastro de Clientes")

    # Campos de cadastro
    tk.Label(root, text="Nome").grid(row=0, column=0)
    nome_var = tk.StringVar()
    tk.Entry(root, textvariable=nome_var).grid(row=0, column=1)

    tk.Label(root, text="CPF|CNPJ").grid(row=1, column=0)
    cpf_var = tk.StringVar()
    cpf_entry = tk.Entry(root, textvariable=cpf_var)
    cpf_entry.grid(row=1, column=1)
    cpf_entry.bind("<KeyRelease>", formatar_documento)  # Vincula a função de formatação do CPF

    tk.Label(root, text="RG").grid(row=2, column=0)
    rg_var = tk.StringVar()
    tk.Entry(root, textvariable=rg_var).grid(row=2, column=1)

    tk.Label(root, text="Nascimento").grid(row=3, column=0)
    nascimento_var = tk.StringVar()
    nascimento_entry = tk.Entry(root, textvariable=nascimento_var)
    nascimento_entry.grid(row=3, column=1)
    nascimento_entry.bind("<KeyRelease>", formatar_nascimento)  # Vincula a função de formatação de data

    tk.Label(root, text="Telefone").grid(row=4, column=0)
    telefones_var = tk.StringVar()
    telefone_entry = tk.Entry(root, textvariable=telefones_var)
    telefone_entry.grid(row=4, column=1)
    telefone_entry.bind("<KeyRelease>", formatar_telefone)

    tk.Label(root, text="CEP").grid(row=5, column=0)
    cep_var = tk.StringVar()
    cep_entry = tk.Entry(root, textvariable=cep_var)
    cep_entry.grid(row=5, column=1)
    cep_entry.bind("<KeyRelease>", formatar_cep)  # Vincula a função de formatação do CEP

    tk.Label(root, text="Complemento|número").grid(row=6, column=0)
    complemento_var = tk.StringVar()
    tk.Entry(root, textvariable=complemento_var).grid(row=6, column=1)

    tk.Label(root, text="E-mail").grid(row=7, column=0)
    email_var = tk.StringVar()  # Certifique-se de que email_var está definida globalmente
    email_entry = tk.Entry(root, textvariable=email_var)
    email_entry.grid(row=7, column=1)

    tk.Label(root, text="Observação").grid(row=1, column=2)
    observacao_var = tk.StringVar()
    observacao_text = tk.Text(root, height=5, width=30)  # Ajuste o tamanho conforme necessário
    observacao_text.grid(row=2, column=2, rowspan=6)  # rowspan para ocupar mais linhas

    # Botão para cadastrar cliente
    tk.Button(root, text="Cadastrar Cliente", command=lambda: (cadastrar_cliente() if validar_nascimento() else None)).grid(row=9, column=1)


    # Botão para excluir cliente
    global botao_excluir
    botao_excluir = tk.Button(root, text="Excluir Cliente", state=tk.DISABLED, command=excluir_cliente)
    botao_excluir.grid(row=10, column=2)

    # Campo de pesquisa
    tk.Label(root, text="Pesquisar Cliente por Nome").grid(row=11, column=0)
    pesquisa_nome_var = tk.StringVar()
    tk.Entry(root, textvariable=pesquisa_nome_var).grid(row=11, column=1)

    # Botão para mostrar clientes semelhantes
    tk.Button(root, text="Buscar Clientes Semelhantes", command=mostrar_clientes_semelhantes).grid(row=11, column=2)
    
    # Botão para editar cliente
    global botao_editar
    botao_editar = tk.Button(root, text="Editar Cliente", state=tk.DISABLED, command=editar_cliente)
    botao_editar.grid(row=9, column=2)

    # Área de Texto
    resultado_texto = tk.Text(root, height=30, width=100)
    resultado_texto.grid(row=12, column=0, columnspan=3, pady=10)

    root.mainloop()

def obter_nomes_clientes():
    return [cliente.nome for cliente in clientes]

def formatar_telefone(event):
    telefone = telefones_var.get().replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
    
    # Limita a entrada a no máximo 11 dígitos
    if len(telefone) > 11:
        telefone = telefone[:11]
    
    # Aplica a formatação de telefone
    if len(telefone) >= 6:
        telefone = f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
    elif len(telefone) >= 3:
        telefone = f"({telefone[:2]}) {telefone[2:]}"
    
    # Atualiza o campo de entrada com o telefone formatado
    telefones_var.set(telefone)
    
    # Move o cursor para a posição correta
    event.widget.icursor(len(telefone))

def formatar_nascimento(event):
    # Obtém o valor do campo de nascimento, removendo qualquer formatação anterior
    nascimento = nascimento_var.get().replace("/", "").strip()

    # Limita a entrada a no máximo 8 dígitos (DDMMAAAA)
    if len(nascimento) > 8:
        nascimento = nascimento[:8]

    # Aplica a formatação DD/MM/AAAA
    if len(nascimento) >= 5:
        nascimento = f"{nascimento[:2]}/{nascimento[2:4]}/{nascimento[4:]}"
    elif len(nascimento) >= 3:
        nascimento = f"{nascimento[:2]}/{nascimento[2:]}"
    
    # Atualiza o campo de entrada com a data formatada
    nascimento_var.set(nascimento)
    
    # Move o cursor para a posição correta
    event.widget.icursor(len(nascimento))

def validar_nascimento():
    data_texto = nascimento_var.get().strip()
    # Se o campo estiver vazio, a validação passa
    if not data_texto:
        return True
    try:
        # Tenta converter a data para o formato DD/MM/AAAA
        datetime.strptime(data_texto, "%d/%m/%Y")
        return True
    except ValueError:
        atualizar_texto("Data de nascimento inválida! Use o formato DD/MM/AAAA e uma data real.")
        return False


if __name__ == "__main__":
    clientes = carregar_clientes()
    criar_interface()
