# app.py

from flask import Flask, jsonify, request, render_template
import json
from datetime import datetime
from urllib.parse import unquote
from dados import FABRICANTES, CATEGORIAS, MODELOS, CORS
from routes_clientes import clientes_bp

app = Flask(__name__)
app.register_blueprint(clientes_bp)

# --- FUNÇÕES AUXILIARES DE ARQUIVO ---
def carregar_dados_do_arquivo(nome_arquivo):
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Se o arquivo não existe ou está vazio, retorna uma estrutura padrão
        if "contador" in nome_arquivo:
            return {'contador_id': 0}
        return []

def salvar_dados_no_arquivo(nome_arquivo, dados):
    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erro ao salvar arquivo {nome_arquivo}: {e}")
        return False

# --- FUNÇÃO CENTRAL DE FILTRAGEM ---
def filtra_propostas(criterios, lista_de_propostas):
    resultados = []
    for proposta in lista_de_propostas:
        compativel = True
        
        # Filtros de texto simples
        for campo in ['categoria', 'fabricante', 'modelo', 'cor']:
            if criterios.get(campo) and criterios[campo] != proposta.get(campo):
                compativel = False
                break
        if not compativel: continue

        # Filtro de Câmbio (Exclusão: Apenas um pode ser selecionado para filtrar)
        manual_desejado = criterios.get('cambio_manual', False)
        automatico_desejado = criterios.get('cambio_automatico', False)
        if manual_desejado and not automatico_desejado and proposta.get('cambio') != 'Manual':
            compativel = False
        if automatico_desejado and not manual_desejado and proposta.get('cambio') != 'Automatico':
            compativel = False
        if not compativel: continue

        # Filtros de intervalo (Ano e Preço)
        try:
            # Ano
            if criterios.get('ano_min') or criterios.get('ano_max'):
                prop_ano_min = int(proposta.get('ano_min') or 0)
                prop_ano_max = int(proposta.get('ano_max') or 9999)
                crit_ano_min = int(criterios.get('ano_min') or 0)
                crit_ano_max = int(criterios.get('ano_max') or 9999)
                if not (prop_ano_max >= crit_ano_min and prop_ano_min <= crit_ano_max):
                    compativel = False
            if not compativel: continue

            # Preço
            if criterios.get('preco_min') or criterios.get('preco_max'):
                prop_preco_min = float(str(proposta.get('preco_min') or 0).replace('.', ''))
                prop_preco_max = float(str(proposta.get('preco_max') or 99999999).replace('.', ''))
                crit_preco_min = float(str(criterios.get('preco_min') or 0).replace('.', ''))
                crit_preco_max = float(str(criterios.get('preco_max') or 99999999).replace('.', ''))
                if not (prop_preco_max >= crit_preco_min and prop_preco_min <= crit_preco_max):
                    compativel = False
        except (ValueError, TypeError):
            compativel = False
        
        if compativel:
            resultados.append(proposta)
    return resultados


# --- ROTAS PRINCIPAIS E DE DADOS ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if data.get('username') == 'admin' and data.get('password') == '1234':
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Usuário ou senha inválidos."}), 401
    
@app.route('/api/dados/fabricantes', methods=['GET'])
def get_fabricantes():
    lista = [{"id": id, "nome": nome} for id, nome in FABRICANTES]
    return jsonify(sorted(lista, key=lambda f: f['nome']))

@app.route('/api/dados/categorias', methods=['GET'])
def get_categorias():
    lista = [{"id": id, "nome": nome} for id, nome in CATEGORIAS]
    return jsonify(sorted(lista, key=lambda c: c['nome']))

@app.route('/api/dados/modelos/<fabricante_nome>', methods=['GET'])
def get_modelos(fabricante_nome):
    modelos = MODELOS.get(fabricante_nome.upper(), [])
    return jsonify(sorted(modelos))

@app.route('/api/dados/cores', methods=['GET'])
def get_cores():
    lista = [{"id": id, "nome": nome} for id, nome in CORS]
    return jsonify(sorted(lista, key=lambda c: c['nome']))


# --- ROTAS DA API DE PROPOSTAS ---

@app.route('/api/propostas/pesquisar', methods=['POST'])
def pesquisar_propostas():
    criterios = request.get_json()
    todas_as_propostas = carregar_dados_do_arquivo('propostas.json')

    tipo_oposto = {"Compra": "Venda", "Venda": "Compra"}.get(criterios.get('tipo'))
    propostas_base = [p for p in todas_as_propostas if p.get('tipo') == tipo_oposto or not criterios.get('tipo')]
    
    resultados_principais = filtra_propostas(criterios, propostas_base)
    ids_ja_encontrados = {p['id'] for p in resultados_principais}

    hot_tips = []
    ordem_relaxamento = [
        {'campo': 'cor', 'label': 'Cor'}, {'campo': 'preco', 'label': 'Preço'}, {'campo': 'ano', 'label': 'Ano'},
        {'campo': 'cambio', 'label': 'Câmbio'}, {'campo': 'modelo', 'label': 'Modelo'},
        {'campo': 'fabricante', 'label': 'Fabricante'}, {'campo': 'categoria', 'label': 'Categoria'},
    ]

    criterios_relaxados = {k: v for k, v in criterios.items() if v}
    labels_relaxados = []

    for item in ordem_relaxamento:
        campo_removido = False
        if item['campo'] == 'preco' and any(k in criterios_relaxados for k in ['preco_min', 'preco_max']):
            criterios_relaxados.pop('preco_min', None); criterios_relaxados.pop('preco_max', None); campo_removido = True
        elif item['campo'] == 'ano' and any(k in criterios_relaxados for k in ['ano_min', 'ano_max']):
            criterios_relaxados.pop('ano_min', None); criterios_relaxados.pop('ano_max', None); campo_removido = True
        elif item['campo'] == 'cambio' and any(k in criterios_relaxados for k in ['cambio_automatico', 'cambio_manual']):
            criterios_relaxados.pop('cambio_automatico', None); criterios_relaxados.pop('cambio_manual', None); campo_removido = True
        elif item['campo'] in criterios_relaxados:
            criterios_relaxados.pop(item['campo'], None); campo_removido = True
        
        if campo_removido:
            labels_relaxados.append(item['label'])
            resultados_parciais = filtra_propostas(criterios_relaxados, propostas_base)
            resultados_novos = [p for p in resultados_parciais if p['id'] not in ids_ja_encontrados]
            
            if resultados_novos:
                resultados_novos.sort(key=lambda p: datetime.strptime(p['data_inclusao'], "%d-%m-%Y"), reverse=True)
                titulo = f"Ignorando {', '.join(labels_relaxados)} ({len(resultados_novos)} encontrados)"
                hot_tips.append({"titulo": titulo, "resultados": resultados_novos})
                ids_ja_encontrados.update({p['id'] for p in resultados_novos})

    return jsonify({
        "resultados_principais": sorted(resultados_principais, key=lambda p: datetime.strptime(p['data_inclusao'], "%d-%m-%Y"), reverse=True),
        "hot_tips": hot_tips
    })

@app.route('/api/propostas/salvar', methods=['POST'])
def salvar_proposta():
    proposta_data = request.get_json()
    proposta_id = proposta_data.get('id')

    if not proposta_data.get('pessoa_empresa') or not proposta_data.get('tipo'):
        return jsonify({"success": False, "message": "Campos 'Tipo' e 'Pessoa/Empresa' são obrigatórios."}), 400

    todas_as_propostas = carregar_dados_do_arquivo('propostas.json')
    mensagem = ""

    if proposta_id:  # ATUALIZAR
        proposta_encontrada = False
        for i, p in enumerate(todas_as_propostas):
            if str(p.get('id')) == str(proposta_id):
                proposta_data['data_inclusao'] = p.get('data_inclusao') # Manter data original
                todas_as_propostas[i] = proposta_data
                proposta_encontrada = True
                break
        if not proposta_encontrada:
            return jsonify({"success": False, "message": f"Proposta ID {proposta_id} não encontrada."}), 404
        mensagem = f"Proposta ID {proposta_id} atualizada com sucesso!"
    else:  # CRIAR
        contador_data = carregar_dados_do_arquivo('contador.json')
        contador_id = contador_data.get('contador_id', 0) + 1
        proposta_data['id'] = str(contador_id)
        proposta_data['data_inclusao'] = datetime.now().strftime("%d-%m-%Y")
        todas_as_propostas.append(proposta_data)
        salvar_dados_no_arquivo('contador.json', {'contador_id': contador_id})
        mensagem = f"Proposta ID {contador_id} salva com sucesso!"

    if salvar_dados_no_arquivo('propostas.json', todas_as_propostas):
        return jsonify({"success": True, "message": mensagem, "proposta": proposta_data})
    else:
        return jsonify({"success": False, "message": "Erro interno ao salvar os dados."}), 500

@app.route('/api/propostas/excluir/<proposta_id>', methods=['DELETE'])
def excluir_proposta(proposta_id):
    todas_as_propostas = carregar_dados_do_arquivo('propostas.json')
    proposta_a_remover = next((p for p in todas_as_propostas if str(p.get('id')) == str(proposta_id)), None)

    if not proposta_a_remover:
        return jsonify({"success": False, "message": "Proposta não encontrada."}), 404

    todas_as_propostas.remove(proposta_a_remover)
    if salvar_dados_no_arquivo('propostas.json', todas_as_propostas):
        return jsonify({"success": True, "message": "Proposta excluída com sucesso."})
    else:
        return jsonify({"success": False, "message": "Erro ao salvar o arquivo."}), 500

@app.route('/api/propostas/por-cliente/<path:nome_cliente>', methods=['GET'])
def propostas_por_cliente(nome_cliente):
    nome_decodificado = unquote(nome_cliente)
    todas_as_propostas = carregar_dados_do_arquivo('propostas.json')
    propostas_do_cliente = [p for p in todas_as_propostas if p.get('pessoa_empresa') == nome_decodificado]
    return jsonify(sorted(propostas_do_cliente, key=lambda p: datetime.strptime(p['data_inclusao'], "%d-%m-%Y"), reverse=True))

@app.route('/api/propostas/<proposta_id>', methods=['GET'])
def get_proposta_por_id(proposta_id):
    todas_as_propostas = carregar_dados_do_arquivo('propostas.json')
    proposta = next((p for p in todas_as_propostas if str(p.get('id')) == str(proposta_id)), None)
    if proposta:
        return jsonify(proposta)
    return jsonify({"message": "Proposta não encontrada"}), 404


if __name__ == '__main__':
    app.run(debug=True)