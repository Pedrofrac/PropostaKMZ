# app.py - VERSÃO COMPLETA E CORRETA

from flask import Flask, jsonify, request, render_template
import json

app = Flask(__name__)

# --- Lógica de Carregamento de Dados ---
def carregar_propostas_do_arquivo():
    try:
        with open('propostas.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# --- Rotas da Aplicação ---

# Rota para a página principal (a interface que o usuário vê)
@app.route('/')
def index():
    return render_template('index.html')

# Rota para a API de login (que o JavaScript vai chamar)
# >>> ESTA É A PARTE QUE ESTAVA FALTANDO <<<
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # Lógica de login SUPER SIMPLES
    if username == 'admin' and password == '1234':
        return jsonify({"success": True, "message": "Login bem-sucedido!"})
    else:
        return jsonify({"success": False, "message": "Usuário ou senha inválidos."}), 401

# Rota da API para obter todas as propostas
@app.route('/api/propostas', methods=['GET'])
def get_propostas():
    propostas = carregar_propostas_do_arquivo()
    return jsonify(propostas)


# --- Bloco para Executar a Aplicação ---
if __name__ == '__main__':
    app.run(debug=True)