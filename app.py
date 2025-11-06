# app.py - VERSÃO DEFINITIVAMENTE COMPLETA

from flask import Flask, jsonify, request, render_template
import json
# Importa TODAS as listas do nosso arquivo de dados, incluindo CORS
from dados import FABRICANTES, CATEGORIAS, MODELOS, CORS

app = Flask(__name__)

# --- FUNÇÕES AUXILIARES ---

def carregar_dados_do_arquivo(nome_arquivo):
    """Carrega dados de um arquivo JSON de forma segura."""
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# --- ROTAS PRINCIPAIS ---

@app.route('/')
def index():
    """Serve a página principal HTML."""
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    """Valida o login."""
    data = request.get_json()
    if data.get('username') == 'admin' and data.get('password') == '1234':
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Usuário ou senha inválidos."}), 401

# --- ROTAS DA API PARA PREENCHER FORMULÁRIOS ---

@app.route('/api/dados/fabricantes', methods=['GET'])
def get_fabricantes():
    """Retorna a lista de fabricantes no formato {id, nome}."""
    lista = [{"id": id, "nome": nome} for id, nome in FABRICANTES]
    return jsonify(sorted(lista, key=lambda f: f['nome']))

@app.route('/api/dados/categorias', methods=['GET'])
def get_categorias():
    """Retorna a lista de categorias no formato {id, nome}."""
    lista = [{"id": id, "nome": nome} for id, nome in CATEGORIAS]
    return jsonify(sorted(lista, key=lambda c: c['nome']))

@app.route('/api/dados/modelos/<fabricante_nome>', methods=['GET'])
def get_modelos(fabricante_nome):
    """Retorna a lista de modelos para um fabricante específico."""
    modelos = MODELOS.get(fabricante_nome.upper(), [])
    return jsonify(sorted(modelos))

@app.route('/api/dados/cores', methods=['GET'])
def get_cores():
    """ << NOVA ROTA >> Retorna a lista de cores no formato {id, nome}."""
    lista = [{"id": id, "nome": nome} for id, nome in CORS]
    return jsonify(sorted(lista, key=lambda c: c['nome']))

# --- ROTAS DA API PARA FUNCIONALIDADES ---

@app.route('/api/propostas/pesquisar', methods=['POST'])
def pesquisar_propostas():
    """Recebe filtros (incluindo cor) e retorna as propostas correspondentes."""
    criterios = request.get_json()
    todas_as_propostas = carregar_dados_do_arquivo('propostas.json')
    resultados = []

    for proposta in todas_as_propostas:
        corresponde = True
        
        # Filtros existentes
        if criterios.get('tipo') and criterios['tipo'] != proposta.get('tipo'): corresponde = False
        if criterios.get('categoria') and criterios['categoria'] != proposta.get('categoria'): corresponde = False
        if criterios.get('fabricante') and criterios['fabricante'] != proposta.get('fabricante'): corresponde = False
        if criterios.get('modelo') and criterios['modelo'] != proposta.get('modelo'): corresponde = False
        if criterios.get('pessoa') and criterios['pessoa'].lower() not in proposta.get('pessoa_empresa', '').lower(): corresponde = False
        
        # << NOVO FILTRO DE COR >>
        if criterios.get('cor') and criterios['cor'].lower() not in proposta.get('cor', '').lower():
             corresponde = False
        
        try:
            # Ano
            prop_ano_min = int(proposta.get('ano_min') or 0); prop_ano_max = int(proposta.get('ano_max') or 9999)
            crit_ano_min = int(criterios.get('ano_min') or 0); crit_ano_max = int(criterios.get('ano_max') or 9999)
            if not (prop_ano_max >= crit_ano_min and prop_ano_min <= crit_ano_max): corresponde = False

            # Preço
            prop_preco_min = float(str(proposta.get('preco_min') or 0).replace('.', '')); prop_preco_max = float(str(proposta.get('preco_max') or 'inf').replace('.', ''))
            crit_preco_min = float(criterios.get('preco_min') or 0); crit_preco_max = float(criterios.get('preco_max') or 'inf')
            if not (prop_preco_max >= crit_preco_min and prop_preco_min <= crit_preco_max): corresponde = False
        except (ValueError, TypeError):
            pass

        if corresponde:
            resultados.append(proposta)
            
    return jsonify(resultados)

# Rota de clientes (pode ser expandida no futuro)
@app.route('/api/clientes/pesquisar', methods=['POST'])
def pesquisar_clientes():
    return jsonify([]) # Desativado temporariamente para focar em propostas

# --- BLOCO DE EXECUÇÃO ---
if __name__ == '__main__':
    app.run(debug=True)