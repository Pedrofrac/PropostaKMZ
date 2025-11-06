// static/app.js - VERSÃO DEFINITIVAMENTE COMPLETA

document.addEventListener('DOMContentLoaded', () => {
    
    // INICIALIZAÇÃO DO AUTOCOMPLETE (SELECT2)
    $(document).ready(function() {
        // Aplica a funcionalidade de busca a todos os selects do formulário de proposta
        $('#prop-categoria, #prop-fabricante, #prop-modelo, #prop-cor').select2({ theme: 'bootstrap-5' });
    });
    
    // MAPEAMENTO DOS ELEMENTOS DA PÁGINA
    const loginArea = document.getElementById('login-area');
    const mainContent = document.getElementById('main-content');
    const passwordInput = document.getElementById('password');
    const loginButton = document.getElementById('login-button');
    const selectFabricante = document.getElementById('prop-fabricante');
    const selectCategoria = document.getElementById('prop-categoria');
    const selectModelo = document.getElementById('prop-modelo');
    const selectCor = document.getElementById('prop-cor'); // << NOVO
    const formProposta = document.getElementById('form-proposta');
    const tbodyPropostas = document.getElementById('resultado-propostas');
    // Mapeamento da aba de clientes para o futuro
    // const formBuscaCliente = document.getElementById('form-busca-cliente');
    // const tbodyClientes = document.getElementById('resultado-clientes');

    // FUNÇÕES GLOBAIS

    async function popularSelect(selectElement, apiUrl, defaultOptionText) {
        try {
            const response = await fetch(apiUrl);
            if (!response.ok) throw new Error('API Error');
            const data = await response.json();
            selectElement.innerHTML = `<option value="">${defaultOptionText}</option>`;
            data.forEach(item => {
                const option = document.createElement('option');
                if (typeof item === 'object' && item !== null) {
                    option.value = item.nome; // Usamos o NOME para consistência
                    option.textContent = item.nome;
                } else {
                    option.value = item;
                    option.textContent = item;
                }
                selectElement.appendChild(option);
            });
        } catch (error) { console.error(`Erro ao popular select ${selectElement.id}:`, error); }
    }

    async function fazerLogin() {
        const username = document.getElementById('username').value;
        const password = passwordInput.value;
        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await response.json();
            if (data.success) {
                loginArea.style.display = 'none';
                mainContent.style.display = 'block';
                // Popula todos os selects iniciais
                await popularSelect(selectFabricante, '/api/dados/fabricantes', 'Todos os Fabricantes');
                await popularSelect(selectCategoria, '/api/dados/categorias', 'Todas as Categorias');
                await popularSelect(selectCor, '/api/dados/cores', 'Todas as Cores'); // << NOVO
                
                // Dispara evento para o Select2 redesenhar os selects
                $(selectFabricante).trigger('change');
                $(selectCategoria).trigger('change');
                $(selectCor).trigger('change'); // << NOVO
            } else { document.getElementById('login-message').textContent = data.message || "Erro"; }
        } catch (error) { document.getElementById('login-message').textContent = "Erro de conexão."; }
    }

    // OUVINTES DE EVENTOS (EVENT LISTENERS)

    loginButton.addEventListener('click', fazerLogin);
    passwordInput.addEventListener('keyup', (event) => { if (event.key === "Enter") fazerLogin(); });

    $(selectFabricante).on('select2:select', async function (e) {
        const fabricanteSelecionado = e.params.data.id;
        selectModelo.innerHTML = '<option value="">Carregando...</option>';
        selectModelo.disabled = true;
        $(selectModelo).val(null).trigger('change');
        if (!fabricanteSelecionado) {
            selectModelo.innerHTML = '<option value="">Escolha um Fabricante</option>';
            return;
        }
        selectModelo.disabled = false;
        await popularSelect(selectModelo, `/api/dados/modelos/${fabricanteSelecionado}`, 'Todos os Modelos');
    });

    formProposta.addEventListener('submit', async (event) => {
        event.preventDefault();
        tbodyPropostas.innerHTML = '<tr><td colspan="9" class="text-center">Buscando...</td></tr>';
        
        // Coleta TODOS os critérios do formulário, incluindo o de COR
        const criterios = {
            tipo: document.getElementById('prop-tipo').value,
            pessoa: document.getElementById('prop-pessoa').value,
            categoria: $(selectCategoria).val(),
            fabricante: $(selectFabricante).val(),
            modelo: $(selectModelo).val(),
            ano_min: document.getElementById('prop-ano-min').value,
            ano_max: document.getElementById('prop-ano-max').value,
            cor: $(selectCor).val(), // << NOVO
            preco_min: document.getElementById('prop-preco-min').value,
            preco_max: document.getElementById('prop-preco-max').value,
        };

        try {
            const response = await fetch('/api/propostas/pesquisar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(criterios)
            });
            const propostas = await response.json();
            
            tbodyPropostas.innerHTML = '';
            if (propostas.length === 0) {
                tbodyPropostas.innerHTML = '<tr><td colspan="9" class="text-center">Nenhuma proposta encontrada.</td></tr>';
            } else {
                propostas.forEach(p => {
                    const tr = document.createElement('tr');
                    // Cria a linha da tabela com TODAS as colunas, incluindo COR
                    tr.innerHTML = `
                        <td>${p.id || ''}</td>
                        <td>${p.data_inclusao || ''}</td>
                        <td><span class="badge bg-primary text-capitalize">${p.tipo || ''}</span></td>
                        <td>${p.fabricante || ''} ${p.modelo || ''}</td>
                        <td>${p.ano_min || ''}-${p.ano_max || ''}</td>
                        <td>${p.cor || ''}</td>
                        <td>R$ ${p.preco_max || '?'}</td>
                        <td>${p.pessoa_empresa || ''}</td>
                        <td>
                            <button class="btn btn-sm btn-warning">Editar</button> 
                            <button class="btn btn-sm btn-danger">Excluir</button>
                        </td>
                    `;
                    tbodyPropostas.appendChild(tr);
                });
            }
        } catch (error) {
            tbodyPropostas.innerHTML = '<tr><td colspan="9" class="text-center text-danger">Erro ao buscar.</td></tr>';
        }
    });

    // A lógica da aba de clientes será adicionada aqui no futuro...

});