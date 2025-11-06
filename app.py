# app.py - VERSÃO FINAL COM CASCATA COMPLETA DE HOT TIPS

from flask import Flask, jsonify, request, render_template
import json
from datetime import datetime
from dados import FABRICANTES, CATEGORIAS, MODELOS, CORS

app = Flask(__name__)

# --- FUNÇÕES AUXILIARES (sem alteração) ---
# ... (as funções carregar_dados_do_arquivo e salvar_dados_no_arquivo permanecem iguais)
def carregar_dados_do_arquivo(nome_arquivo):
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as f: return json.load(f)
    except: return []
def salvar_dados_no_arquivo(nome_arquivo, dados):
    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as f: json.dump(dados, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erro ao salvar arquivo {nome_arquivo}: {e}"); return False

# --- FUNÇÃO CENTRAL DE FILTRAGEM (sem alteração) ---
def filtra_propostas(criterios, lista_de_propostas):
    # ... (esta função já está correta e será reutilizada)
    resultados = []
    criterios_sem_pessoa = criterios.copy(); criterios_sem_pessoa.pop('pessoa', None)
    for proposta in lista_de_propostas:
        compativel = True
        for campo in ['categoria', 'fabricante', 'modelo', 'cor']:
            if criterios_sem_pessoa.get(campo) and criterios_sem_pessoa[campo] != proposta.get(campo): compativel = False; break
        if not compativel: continue
        if criterios.get('cambio_manual') and proposta.get('cambio') != 'Manual': compativel = False
        if criterios.get('cambio_automatico') and proposta.get('cambio') != 'Automatico': compativel = False
        if not compativel: continue
        try:
            if criterios.get('ano_min') or criterios.get('ano_max'):
                if proposta.get('ano_min') or proposta.get('ano_max'):
                    prop_ano_min = int(proposta.get('ano_min') or 0); prop_ano_max = int(proposta.get('ano_max') or 9999)
                    crit_ano_min = int(criterios.get('ano_min') or 0); crit_ano_max = int(criterios.get('ano_max') or 9999)
                    if not (prop_ano_max >= crit_ano_min and prop_ano_min <= crit_ano_max): compativel = False
                else: compativel = False
            if not compativel: continue
            if criterios.get('preco_min') or criterios.get('preco_max'):
                if proposta.get('preco_min') or proposta.get('preco_max'):
                    prop_preco_min = float(str(proposta.get('preco_min') or 0).replace('.', ''))
                    prop_preco_max = float(str(proposta.get('preco_max') or 99999999).replace('.', ''))
                    crit_preco_min = float(str(criterios.get('preco_min') or 0).replace('.', ''))
                    crit_preco_max = float(str(criterios.get('preco_max') or 99999999).replace('.', ''))
                    if not (prop_preco_max >= crit_preco_min and prop_preco_min <= crit_preco_max): compativel = False
        except (ValueError, TypeError): compativel = False
        if compativel: resultados.append(proposta)
    return resultados

# --- ROTAS (sem alteração, exceto a de pesquisa) ---
@app.route('/')
def index(): return render_template('index.html')
# ... (as rotas /login e /api/dados/* permanecem iguais)
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if data.get('username') == 'admin' and data.get('password') == '1234': return jsonify({"success": True})
    return jsonify({"success": False, "message": "Usuário ou senha inválidos."}), 401
@app.route('/api/dados/fabricantes', methods=['GET'])
def get_fabricantes():
    lista = [{"id": id, "nome": nome} for id, nome in FABRICANTES]; return jsonify(sorted(lista, key=lambda f: f['nome']))
@app.route('/api/dados/categorias', methods=['GET'])
def get_categorias():
    lista = [{"id": id, "nome": nome} for id, nome in CATEGORIAS]; return jsonify(sorted(lista, key=lambda c: c['nome']))
@app.route('/api/dados/modelos/<fabricante_nome>', methods=['GET'])
def get_modelos(fabricante_nome):
    modelos = MODELOS.get(fabricante_nome.upper(), []); return jsonify(sorted(modelos))
@app.route('/api/dados/cores', methods=['GET'])
def get_cores():
    lista = [{"id": id, "nome": nome} for id, nome in CORS]; return jsonify(sorted(lista, key=lambda c: c['nome']))


# --- ROTA DE PESQUISA (COM A LÓGICA COMPLETA DE HOT TIPS) ---
@app.route('/api/propostas/pesquisar', methods=['POST'])
def pesquisar_propostas():
    criterios = request.get_json()
    todas_as_propostas = carregar_dados_do_arquivo('propostas.json')

    tipo_criterio = criterios.get('tipo')
    if tipo_criterio == "Compra": tipos_a_buscar = ["Venda"]
    elif tipo_criterio == "Venda": tipos_a_buscar = ["Compra"]
    else: tipos_a_buscar = ["Compra", "Venda"]
    
    propostas_base = [p for p in todas_as_propostas if p.get('tipo') in tipos_a_buscar]
    
    # 1. Executa a pesquisa principal com todos os filtros
    resultados_principais = filtra_propostas(criterios, propostas_base)
    ids_ja_encontrados = {p['id'] for p in resultados_principais}

    # 2. Prepara para os Hot Tips
    hot_tips = []
    
    # A ordem de importância dos filtros a serem relaxados
    ordem_relaxamento = [
        {'campo': 'cor', 'label': 'Cor'},
        {'campo': 'preco', 'label': 'Preço'},
        {'campo': 'ano', 'label': 'Ano'},
        {'campo': 'cambio', 'label': 'Câmbio'},
        {'campo': 'modelo', 'label': 'Modelo'},
        {'campo': 'fabricante', 'label': 'Fabricante'},
        {'campo': 'categoria', 'label': 'Categoria'},
    ]

    criterios_relaxados = criterios.copy()
    labels_relaxados = []

    for item in ordem_relaxamento:
        # Remove o filtro atual da lista de critérios
        if item['campo'] == 'preco':
            criterios_relaxados.pop('preco_min', None)
            criterios_relaxados.pop('preco_max', None)
        elif item['campo'] == 'ano':
            criterios_relaxados.pop('ano_min', None)
            criterios_relaxados.pop('ano_max', None)
        elif item['campo'] == 'cambio':
            criterios_relaxados.pop('cambio_automatico', None)
            criterios_relaxados.pop('cambio_manual', None)
        else:
            criterios_relaxados.pop(item['campo'], None)
        
        labels_relaxados.append(item['label'])

        # Só executa a busca se o critério removido realmente existia
        if any(criterios.get(key) for key in ['cor', 'preco_min', 'preco_max', 'ano_min', 'ano_max', 'cambio_automatico', 'cambio_manual', 'modelo', 'fabricante', 'categoria']):
            resultados_parciais = filtra_propostas(criterios_relaxados, propostas_base)
            
            # Pega apenas os resultados que ainda não foram mostrados
            resultados_novos = [p for p in resultados_parciais if p['id'] not in ids_ja_encontrados]
            
            if resultados_novos:
                titulo = f"Ignorando {', '.join(labels_relaxados)} ({len(resultados_novos)} encontrados)"
                hot_tips.append({
                    "titulo": titulo,
                    "resultados": resultados_novos
                })
                # Adiciona os novos IDs à lista de já encontrados para evitar duplicatas no próximo Hot Tip
                ids_ja_encontrados.update({p['id'] for p in resultados_novos})

    # 3. Monta a resposta final
    resposta_final = {
        "resultados_principais": sorted(resultados_principais, key=lambda p: datetime.strptime(p['data_inclusao'], "%d-%m-%Y"), reverse=True),
        "hot_tips": hot_tips
    }
    
    return jsonify(resposta_final)

# --- ROTA PARA SALVAR (sem alteração) ---
@app.route('/api/propostas/salvar', methods=['POST'])
def salvar_proposta():
    # ... (código para salvar a proposta permanece o mesmo) ...
    nova_proposta = request.get_json()
    if nova_proposta.get('tipo') == 'Venda':
        campos_obrigatorios = ['pessoa_empresa', 'categoria', 'fabricante', 'modelo', 'cor', 'cambio']
        for campo in campos_obrigatorios:
            if not nova_proposta.get(campo): return jsonify({"mensagem": f"Erro: O campo '{campo}' é obrigatório para Venda."}), 400
        ano_min = nova_proposta.get('ano_min'); ano_max = nova_proposta.get('ano_max')
        if ano_min and ano_max and ano_min != ano_max: return jsonify({"mensagem": "Erro: Ano Mínimo e Máximo devem ser iguais para Venda."}), 400
        elif ano_min and not ano_max: nova_proposta['ano_max'] = ano_min
        elif not ano_min and ano_max: nova_proposta['ano_min'] = ano_max
        elif not ano_min and not ano_max: return jsonify({"mensagem": "Erro: O campo 'Ano' é obrigatório para Venda."}), 400
        preco_min = nova_proposta.get('preco_min'); preco_max = nova_proposta.get('preco_max')
        if preco_min and not preco_max: nova_proposta['preco_max'] = preco_min
        elif not preco_min and preco_max: nova_proposta['preco_min'] = preco_max
    if not nova_proposta.get('tipo') or not nova_proposta.get('pessoa_empresa'): return jsonify({"mensagem": "Erro: 'Tipo' e 'Pessoa/Empresa' são obrigatórios."}), 400
    todas_as_propostas = carregar_dados_do_arquivo('propostas.json')
    contador_data = carregar_dados_do_arquivo('contador.json'); contador_id = contador_data.get('contador_id', 0)
    contador_id += 1; nova_proposta['id'] = str(contador_id)
    nova_proposta['data_inclusao'] = datetime.now().strftime("%d-%m-%Y")
    todas_as_propostas.append(nova_proposta)
    if not salvar_dados_no_arquivo('propostas.json', todas_as_propostas) or \
       not salvar_dados_no_arquivo('contador.json', {'contador_id': contador_id}):
        return jsonify({"mensagem": "Erro interno ao salvar arquivos."}), 500
    propostas_compatíveis = []
    tipo_oposto = 'Compra' if nova_proposta.get('tipo') == 'Venda' else 'Venda'
    for p in todas_as_propostas:
        if p.get('tipo') == tipo_oposto and p.get('fabricante') == nova_proposta.get('fabricante') and p.get('modelo') == nova_proposta.get('modelo'):
            propostas_compatíveis.append(p)
    return jsonify({"mensagem": f"Proposta ID {contador_id} salva com sucesso!", "propostas_compatíveis": propostas_compatíveis})

# --- BLOCO DE EXECUÇÃO ---
if __name__ == '__main__':
    app.run(debug=True)