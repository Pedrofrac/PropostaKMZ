# routes_clientes.py

from flask import Blueprint, jsonify, request
import json

clientes_bp = Blueprint('clientes', __name__, url_prefix='/api/clientes')
CLIENTES_FILE = 'clientes.json'

def carregar_dados(arquivo):
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def salvar_dados(arquivo, dados):
    try:
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erro ao salvar o arquivo {arquivo}: {e}")
        return False

@clientes_bp.route('/listar', methods=['GET'])
def listar_clientes():
    clientes = carregar_dados(CLIENTES_FILE)
    return jsonify(sorted(clientes, key=lambda c: c.get('nome', '').lower()))

@clientes_bp.route('/listar-nomes', methods=['GET'])
def listar_nomes_clientes():
    clientes = carregar_dados(CLIENTES_FILE)
    nomes = [{"id": c['nome'], "nome": c['nome']} for c in clientes if c.get('nome')]
    return jsonify(sorted(nomes, key=lambda c: c['nome'].lower()))

@clientes_bp.route('/salvar', methods=['POST'])
def salvar_cliente():
    cliente_data = request.get_json()
    if not cliente_data or not cliente_data.get('nome'):
        return jsonify({"success": False, "message": "O nome do cliente é obrigatório."}), 400

    clientes = carregar_dados(CLIENTES_FILE)
    cliente_id = cliente_data.get('id')

    if cliente_id:  # Atualização
        cliente_encontrado = False
        for i, cliente in enumerate(clientes):
            if cliente.get('id') == cliente_id:
                clientes[i] = cliente_data
                cliente_encontrado = True
                break
        if not cliente_encontrado:
            return jsonify({"success": False, "message": "Cliente não encontrado para atualização."}), 404
        message = "Cliente atualizado com sucesso!"
    else:  # Criação
        novo_id = max([c.get('id', 0) for c in clientes] or [0]) + 1
        cliente_data['id'] = novo_id
        clientes.append(cliente_data)
        message = "Cliente cadastrado com sucesso!"

    if salvar_dados(CLIENTES_FILE, clientes):
        return jsonify({"success": True, "message": message, "cliente": cliente_data})
    else:
        return jsonify({"success": False, "message": "Erro ao salvar os dados."}), 500

@clientes_bp.route('/excluir/<int:cliente_id>', methods=['DELETE'])
def excluir_cliente(cliente_id):
    clientes = carregar_dados(CLIENTES_FILE)
    cliente_a_remover = next((c for c in clientes if c.get('id') == cliente_id), None)
    
    if cliente_a_remover:
        clientes.remove(cliente_a_remover)
        if salvar_dados(CLIENTES_FILE, clientes):
            return jsonify({"success": True, "message": "Cliente excluído com sucesso."})
        else:
            return jsonify({"success": False, "message": "Erro ao salvar dados após a exclusão."}), 500
    else:
        return jsonify({"success": False, "message": "Cliente não encontrado."}), 404