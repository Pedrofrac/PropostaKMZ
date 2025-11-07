// static/app.js - VERSÃO FINAL COM PESQUISA AUTOMÁTICA E HOT TIPS

document.addEventListener('DOMContentLoaded', () => {
    
    // INICIALIZAÇÃO DO AUTOCOMPLETE (SELECT2)
    $(document).ready(function() {
        $('#prop-categoria, #prop-fabricante, #prop-modelo, #prop-cor').select2({ theme: 'bootstrap-5' });
    });
    
    // MAPEAMENTO DE TODOS OS ELEMENTOS
    const loginArea = document.getElementById('login-area');
    const mainContent = document.getElementById('main-content');
    const passwordInput = document.getElementById('password');
    const loginButton = document.getElementById('login-button');
    const formProposta = document.getElementById('form-proposta');
    const tbodyPropostas = document.getElementById('resultado-propostas');
    const btnSalvarProposta = document.querySelector('#form-proposta .btn-success');
    const btnLimparFiltros = document.getElementById('btn-limpar-filtros');
    const hotTipsAccordion = document.getElementById('hot-tips-accordion');
    const camposDeFiltro = document.querySelectorAll('.filtro-auto');

    // --- FUNÇÕES ---

    async function popularSelect(selectElement, apiUrl, defaultOptionText) {
        // ... (código sem alteração)
        try {
            const response = await fetch(apiUrl);
            if (!response.ok) throw new Error('API Error');
            const data = await response.json();
            selectElement.innerHTML = `<option value="">${defaultOptionText}</option>`;
            data.forEach(item => {
                const option = document.createElement('option');
                if (typeof item === 'object' && item !== null) {
                    option.value = item.nome;
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
        // ... (código sem alteração)
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
                await popularSelect(document.getElementById('prop-fabricante'), '/api/dados/fabricantes', 'Todos os Fabricantes');
                await popularSelect(document.getElementById('prop-categoria'), '/api/dados/categorias', 'Todas as Categorias');
                await popularSelect(document.getElementById('prop-cor'), '/api/dados/cores', 'Todas as Cores');
            } else { document.getElementById('login-message').textContent = data.message || "Erro"; }
        } catch (error) { document.getElementById('login-message').textContent = "Erro de conexão."; }
    }

    function renderizarTabela(tbodyElement, propostas, mensagemNenhumResultado = "Nenhuma proposta encontrada.") {
        // ... (código sem alteração)
        tbodyElement.innerHTML = '';
        if (!propostas || propostas.length === 0) {
            const colunas = tbodyElement.closest('table').querySelector('thead tr').childElementCount;
            tbodyElement.innerHTML = `<tr><td colspan="${colunas}" class="text-center">${mensagemNenhumResultado}</td></tr>`;
            return;
        }
        propostas.forEach(p => {
            const tipoLower = (p.tipo || '').toLowerCase();
            let corBadge = (tipoLower === 'compra') ? 'bg-primary' : (tipoLower === 'venda') ? 'bg-success' : 'bg-secondary';
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${p.id || ''}</td><td>${p.data_inclusao || ''}</td><td><span class="badge ${corBadge} text-capitalize">${p.tipo || ''}</span></td><td>${p.fabricante || ''} ${p.modelo || ''}</td><td>${p.ano_min || ''}-${p.ano_max || ''}</td><td>${p.cor || ''}</td><td>R$ ${p.preco_max || '?'}</td><td>${p.pessoa_empresa || ''}</td><td><button class="btn btn-sm btn-warning">Editar</button> <button class="btn btn-sm btn-danger">Excluir</button></td>`;
            tbodyElement.appendChild(tr);
        });
    }

    /**
     * Função principal que dispara a pesquisa automática.
     */
    async function dispararPesquisa() {
        tbodyPropostas.innerHTML = '<tr><td colspan="9" class="text-center">Buscando...</td></tr>';
        hotTipsAccordion.innerHTML = '';
        
        const criterios = {
            tipo: document.getElementById('prop-tipo').value,
            categoria: $('#prop-categoria').val(),
            fabricante: $('#prop-fabricante').val(),
            modelo: $('#prop-modelo').val(),
            ano_min: document.getElementById('prop-ano-min').value,
            ano_max: document.getElementById('prop-ano-max').value,
            cor: $('#prop-cor').val(),
            preco_min: document.getElementById('prop-preco-min').value,
            preco_max: document.getElementById('prop-preco-max').value,
            cambio_automatico: document.getElementById('cambio-automatico').checked,
            cambio_manual: document.getElementById('cambio-manual').checked,
        };

        try {
            const response = await fetch('/api/propostas/pesquisar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(criterios)
            });
            const dados = await response.json();
            
            renderizarTabela(tbodyPropostas, dados.resultados_principais);

            if (dados.hot_tips && dados.hot_tips.length > 0) {
                dados.hot_tips.forEach((tip, index) => {
                    const tipId = `hot-tip-${index}`;
                    const accordionItem = document.createElement('div');
                    accordionItem.className = 'accordion-item';
                    accordionItem.innerHTML = `
                        <h2 class="accordion-header" id="heading-${tipId}">
                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-${tipId}">
                                ${tip.titulo}
                            </button>
                        </h2>
                        <div id="collapse-${tipId}" class="accordion-collapse collapse" data-bs-parent="#hot-tips-accordion">
                            <div class="accordion-body">
                                <table class="table table-sm table-hover">
                                    <thead><tr><th>ID</th><th>Data</th><th>Tipo</th><th>Veículo</th><th>Ano</th><th>Cor</th><th>Preço</th><th>Anunciante</th></tr></thead>
                                    <tbody id="tbody-${tipId}"></tbody>
                                </table>
                            </div>
                        </div>
                    `;
                    hotTipsAccordion.appendChild(accordionItem);
                    renderizarTabela(document.getElementById(`tbody-${tipId}`), tip.resultados);
                });
            }

        } catch (error) {
            tbodyPropostas.innerHTML = '<tr><td colspan="9" class="text-center text-danger">Erro ao buscar.</td></tr>';
            console.error("Erro na pesquisa:", error);
        }
    }

    // --- OUVINTES DE EVENTOS (EVENT LISTENERS) ---

    loginButton.addEventListener('click', fazerLogin);
    passwordInput.addEventListener('keyup', (event) => { if (event.key === "Enter") fazerLogin(); });
    
    camposDeFiltro.forEach(campo => {
        if (campo.type === 'number' || campo.type === 'text') {
            campo.addEventListener('keyup', dispararPesquisa);
        } else {
            campo.addEventListener('change', dispararPesquisa);
        }
    });
    $('#prop-categoria, #prop-fabricante, #prop-modelo, #prop-cor').on('select2:select select2:clear', dispararPesquisa);

    $('#prop-fabricante').on('select2:select', async function (e) {
        const fabricanteSelecionado = e.params.data.id;
        const selectModelo = document.getElementById('prop-modelo');
        selectModelo.innerHTML = '<option value="">Carregando...</option>';
        selectModelo.disabled = true;
        if (!fabricanteSelecionado) {
            selectModelo.innerHTML = '<option value="">Escolha um Fabricante</option>';
            return;
        }
        selectModelo.disabled = false;
        await popularSelect(selectModelo, `/api/dados/modelos/${fabricanteSelecionado}`, 'Todos os Modelos');
    });

    btnLimparFiltros.addEventListener('click', () => {
        formProposta.reset();
        $('#prop-categoria, #prop-fabricante, #prop-modelo, #prop-cor').val(null).trigger('change');
        dispararPesquisa();
    });

    btnSalvarProposta.addEventListener('click', async () => {
        // ... (código existente para salvar proposta, sem alteração)
        // ...
        let novaProposta = {
            tipo: document.getElementById('prop-tipo').value,
            pessoa_empresa: document.getElementById('prop-pessoa').value,
            categoria: $('#prop-categoria').val(),
            fabricante: $('#prop-fabricante').val(),
            modelo: $('#prop-modelo').val(),
            ano_min: document.getElementById('prop-ano-min').value,
            ano_max: document.getElementById('prop-ano-max').value,
            cor: $('#prop-cor').val(),
            preco_min: document.getElementById('prop-preco-min').value,
            preco_max: document.getElementById('prop-preco-max').value,
            cambio: document.getElementById('cambio-automatico').checked ? 'Automatico' : (document.getElementById('cambio-manual').checked ? 'Manual' : '')
        };
        // ... (resto do código de validação e salvamento)
        if (novaProposta.tipo === 'Venda') {
            if (!novaProposta.pessoa_empresa || !novaProposta.categoria || !novaProposta.fabricante || !novaProposta.modelo || !novaProposta.cor) { alert('Para Venda, todos os campos (exceto Preço e Câmbio) são obrigatórios.'); return; }
            if (novaProposta.ano_min && novaProposta.ano_max && novaProposta.ano_min !== novaProposta.ano_max) { alert('Para Venda, o Ano Mínimo e Máximo devem ser iguais.'); return; }
            else if (novaProposta.ano_min && !novaProposta.ano_max) { novaProposta.ano_max = novaProposta.ano_min; }
            else if (!novaProposta.ano_min && novaProposta.ano_max) { novaProposta.ano_min = novaProposta.ano_max; }
            else if (!novaProposta.ano_min && !novaProposta.ano_max) { alert('Para Venda, o campo Ano é obrigatório.'); return; }
            if (novaProposta.preco_min && !novaProposta.preco_max) { novaProposta.preco_max = novaProposta.preco_min; }
            else if (!novaProposta.preco_min && novaProposta.preco_max) { novaProposta.preco_min = novaProposta.preco_max; }
        }
        if (!novaProposta.tipo || !novaProposta.pessoa_empresa) { alert('Por favor, preencha pelo menos os campos "Tipo" e "Pessoa/Empresa".'); return; }
        try {
            const response = await fetch('/api/propostas/salvar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(novaProposta)
            });
            if (!response.ok) throw new Error('Falha ao salvar a proposta.');
            const resultado = await response.json();
            alert(resultado.mensagem);
            btnLimparFiltros.click();
            renderizarTabela(tbodyPropostas, resultado.propostas_compatíveis, "Nenhuma proposta compatível encontrada após o cadastro.");
        } catch (error) {
            console.error('Erro:', error);
            alert('Ocorreu um erro ao tentar salvar a proposta.');
        }
    });
});