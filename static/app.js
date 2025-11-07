// static/app.js

/**
 * Função global para ser chamada de outros scripts (como clientes.js).
 * Busca uma proposta por ID, troca para a aba de propostas e preenche o formulário para edição.
 * @param {string} propostaId - O ID da proposta a ser carregada.
 */
async function carregarPropostaParaEdicao(propostaId) {
    try {
        const response = await fetch(`/api/propostas/${propostaId}`);
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.message || 'Proposta não encontrada.');
        }
        
        const proposta = await response.json();
        
        const tabPropostas = document.getElementById('tab-propostas');
        if (tabPropostas) {
            new bootstrap.Tab(tabPropostas).show();
        }

        preencherFormularioProposta(proposta);
    } catch (error) {
        console.error("Erro ao carregar proposta para edição:", error);
        alert(error.message);
    }
}

/**
 * Função global que preenche o formulário de propostas com os dados de um objeto.
 * @param {object} proposta - O objeto da proposta com todos os seus campos.
 */
function preencherFormularioProposta(proposta) {
    const form = document.getElementById('form-proposta');
    const idInput = document.getElementById('prop-id');
    const btnSalvar = document.getElementById('btn-salvar-proposta');

    form.reset();
    $('#prop-categoria, #prop-fabricante, #prop-modelo, #prop-cor, #prop-pessoa').val(null).trigger('change');
    
    idInput.value = proposta.id;
    document.getElementById('prop-tipo').value = proposta.tipo || '';
    $('#prop-pessoa').val(proposta.pessoa_empresa).trigger('change');
    $('#prop-categoria').val(proposta.categoria).trigger('change');
    $('#prop-cor').val(proposta.cor).trigger('change');
    
    document.getElementById('cambio-automatico').checked = proposta.cambio === 'Automatico';
    document.getElementById('cambio-manual').checked = proposta.cambio === 'Manual';
    
    document.getElementById('prop-ano-min').value = proposta.ano_min || '';
    document.getElementById('prop-ano-max').value = proposta.ano_max || '';
    document.getElementById('prop-preco-min').value = proposta.preco_min || '';
    document.getElementById('prop-preco-max').value = proposta.preco_max || '';
    document.getElementById('prop-obs').value = proposta.observacoes || '';

    const selectModelo = document.getElementById('prop-modelo');
    if (proposta.fabricante) {
        selectModelo.disabled = true;
        $('#prop-fabricante').val(proposta.fabricante).trigger('change');

        setTimeout(() => {
            $('#prop-modelo').val(proposta.modelo).trigger('change');
            selectModelo.disabled = false;
        }, 500);
    }

    btnSalvar.textContent = `Atualizar ID ${proposta.id}`;
    btnSalvar.classList.replace('btn-success', 'btn-primary');
    window.scrollTo(0, 0);
}

document.addEventListener('DOMContentLoaded', () => {
    // MAPEAMENTO DE ELEMENTOS
    const loginArea = document.getElementById('login-area'), mainContent = document.getElementById('main-content');
    const passwordInput = document.getElementById('password'), loginButton = document.getElementById('login-button');
    const formProposta = document.getElementById('form-proposta'), tbodyPropostas = document.getElementById('resultado-propostas');
    const btnSalvarProposta = document.getElementById('btn-salvar-proposta'), btnLimparFiltros = document.getElementById('btn-limpar-filtros');
    const hotTipsAccordion = document.getElementById('hot-tips-accordion');
    
    $('#prop-categoria, #prop-fabricante, #prop-modelo, #prop-cor, #prop-pessoa').select2({
        theme: 'bootstrap-5'
    });

    // FUNÇÕES
    window.popularSelect = async (selectElement, apiUrl, defaultOptionText) => {
        try {
            const response = await fetch(apiUrl);
            if (!response.ok) throw new Error('API Error');
            const data = await response.json();
            const selectedValue = $(selectElement).val(); 
            selectElement.innerHTML = `<option value="">${defaultOptionText}</option>`;
            data.forEach(item => {
                const option = document.createElement('option');
                option.value = item.nome || item;
                option.textContent = item.nome || item;
                selectElement.appendChild(option);
            });
            $(selectElement).val(selectedValue).trigger('change.select2');
        } catch (error) { console.error(`Erro ao popular select ${selectElement.id}:`, error); }
    };
    
    const limparFormularioProposta = () => {
        formProposta.reset();
        document.getElementById('prop-id').value = '';
        $('#prop-categoria, #prop-fabricante, #prop-modelo, #prop-cor, #prop-pessoa').val(null).trigger('change');
        document.getElementById('prop-modelo').disabled = true;
        btnSalvarProposta.textContent = 'Salvar';
        btnSalvarProposta.classList.replace('btn-primary', 'btn-success');
        dispararPesquisa();
    };

    const renderizarTabela = (tbody, propostas, isSuggestion = false) => {
        const colspan = isSuggestion ? 11 : 12;
        tbody.innerHTML = '';
        if (!propostas || propostas.length === 0) {
            tbody.innerHTML = `<tr><td colspan="${colspan}" class="text-center">Nenhuma proposta encontrada.</td></tr>`;
            return;
        }
        propostas.forEach(p => {
            const tr = document.createElement('tr');
            tr.dataset.proposta = JSON.stringify(p);
            
            const ano = (p.ano_min && p.ano_max && p.ano_min !== p.ano_max) ? `${p.ano_min}-${p.ano_max}` : (p.ano_min || p.ano_max || '');
            
            // CORREÇÃO: Lógica para formatar o preço, garantindo que valores vazios resultem em string vazia.
            let precoExibido = '';
            const precoMinF = p.preco_min ? new Intl.NumberFormat('pt-BR').format(p.preco_min) : '';
            const precoMaxF = p.preco_max ? new Intl.NumberFormat('pt-BR').format(p.preco_max) : '';
            if (precoMinF && precoMaxF) {
                precoExibido = (precoMinF === precoMaxF) ? precoMaxF : `${precoMinF} - ${precoMaxF}`;
            } else if (precoMinF) {
                precoExibido = precoMinF;
            } else if (precoMaxF) {
                precoExibido = precoMaxF;
            }

            const badge = `<span class="badge bg-${p.tipo === 'Compra' ? 'primary' : 'success'} text-capitalize">${p.tipo}</span>`;
            const obsIcon = p.observacoes ? `<i class="bi bi-info-circle ms-1"></i>` : '';

            let cols = `<td>${p.id}</td><td>${p.data_inclusao}</td><td>${badge}</td><td>${p.categoria||''}</td><td>${p.fabricante||''}</td><td>${p.modelo||''}</td><td>${p.cambio||''}</td><td>${ano}</td><td>${precoExibido}</td><td>${p.cor||''}</td><td data-bs-toggle="tooltip" title="${p.observacoes||'Sem observações.'}">${p.pessoa_empresa||''} ${obsIcon}</td>`;
            if (!isSuggestion) {
                cols += `<td><button class="btn btn-sm btn-warning btn-editar-proposta">Editar</button> <button class="btn btn-sm btn-danger btn-excluir-proposta" data-id="${p.id}">Excluir</button></td>`;
            }
            tr.innerHTML = cols;
            tbody.appendChild(tr);
        });
        [...tbody.querySelectorAll('[data-bs-toggle="tooltip"]')].map(el => new bootstrap.Tooltip(el));
    };

    const dispararPesquisa = async () => {
        tbodyPropostas.innerHTML = `<tr><td colspan="12" class="text-center">Buscando...</td></tr>`;
        hotTipsAccordion.innerHTML = '';
        
        const criterios = {
            tipo: document.getElementById('prop-tipo').value, categoria: $('#prop-categoria').val(), fabricante: $('#prop-fabricante').val(), modelo: $('#prop-modelo').val(),
            ano_min: document.getElementById('prop-ano-min').value, ano_max: document.getElementById('prop-ano-max').value, cor: $('#prop-cor').val(),
            preco_min: document.getElementById('prop-preco-min').value, preco_max: document.getElementById('prop-preco-max').value,
            cambio_automatico: document.getElementById('cambio-automatico').checked, cambio_manual: document.getElementById('cambio-manual').checked,
        };
        try {
            const response = await fetch('/api/propostas/pesquisar', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(criterios) });
            const data = await response.json();
            renderizarTabela(tbodyPropostas, data.resultados_principais, false);
            
            if (data.hot_tips && data.hot_tips.length > 0) {
                let accordionHTML = '';
                data.hot_tips.forEach((tip, index) => {
                    const id = `tip-${index}`;
                    accordionHTML += `<div class="accordion-item"><h2 class="accordion-header"><button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-${id}">${tip.titulo}</button></h2><div id="collapse-${id}" class="accordion-collapse collapse" data-bs-parent="#hot-tips-accordion"><div class="accordion-body p-2"><div class="table-responsive"><table class="table table-sm table-hover mb-0"><thead><tr><th>ID</th><th>Data</th><th>Tipo</th><th>Categoria</th><th>Fabricante</th><th>Modelo</th><th>Câmbio</th><th>Ano</th><th>Preço</th><th>Cor</th><th>Anunciante</th></tr></thead><tbody id="tbody-${id}"></tbody></table></div></div></div></div>`;
                });
                hotTipsAccordion.innerHTML = accordionHTML;
                data.hot_tips.forEach((tip, index) => {
                    renderizarTabela(document.getElementById(`tbody-tip-${index}`), tip.resultados, true);
                });
            }
        } catch (error) { 
            console.error("Erro na pesquisa:", error);
            tbodyPropostas.innerHTML = `<tr><td colspan="12" class="text-danger text-center">Ocorreu um erro ao buscar os dados.</td></tr>`;
        }
    };
    
    const configurarGatilhosPesquisa = () => {
        document.querySelectorAll('.filtro-auto').forEach(el => {
            if (el.matches('input[type="number"]')) {
                el.addEventListener('keyup', dispararPesquisa);
            } else if (el.matches('input[type="checkbox"]')) {
                el.addEventListener('change', () => {
                    if(el.id === 'cambio-automatico' && el.checked) document.getElementById('cambio-manual').checked = false;
                    if(el.id === 'cambio-manual' && el.checked) document.getElementById('cambio-automatico').checked = false;
                    dispararPesquisa();
                });
            } else { // Selects
                el.addEventListener('change', dispararPesquisa);
            }
        });
        
        $('#prop-fabricante, #prop-modelo, #prop-categoria, #prop-cor').on('select2:select select2:unselect select2:clear', dispararPesquisa);
        
        $('#prop-fabricante').on('change', function () {
            const fab = $(this).val();
            const selectModelo = document.getElementById('prop-modelo');
            
            if (!fab) {
                selectModelo.innerHTML = '<option value="">Escolha um Fabricante</option>';
                selectModelo.disabled = true;
            } else {
                selectModelo.disabled = false;
                popularSelect(selectModelo, `/api/dados/modelos/${fab}`, 'Todos os Modelos');
            }
            $(selectModelo).val(null).trigger('change');
        });
    };

    btnLimparFiltros.addEventListener('click', limparFormularioProposta);

    btnSalvarProposta.addEventListener('click', async () => {
        const proposta = {
            id: document.getElementById('prop-id').value || null,
            tipo: document.getElementById('prop-tipo').value,
            pessoa_empresa: $('#prop-pessoa').val(),
            categoria: $('#prop-categoria').val(),
            fabricante: $('#prop-fabricante').val(),
            modelo: $('#prop-modelo').val(),
            cambio: document.getElementById('cambio-automatico').checked ? 'Automatico' : (document.getElementById('cambio-manual').checked ? 'Manual' : ''),
            ano_min: document.getElementById('prop-ano-min').value,
            ano_max: document.getElementById('prop-ano-max').value,
            preco_min: document.getElementById('prop-preco-min').value,
            preco_max: document.getElementById('prop-preco-max').value,
            cor: $('#prop-cor').val(),
            observacoes: document.getElementById('prop-obs').value
        };
        try {
            const response = await fetch('/api/propostas/salvar', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(proposta) });
            const resultado = await response.json();
            if (!resultado.success) throw new Error(resultado.message);
            alert(resultado.message);
            limparFormularioProposta();
        } catch (error) { alert(`Erro: ${error.message}`); }
    });

    tbodyPropostas.addEventListener('click', async (e) => {
        const btnEditar = e.target.closest('.btn-editar-proposta');
        const btnExcluir = e.target.closest('.btn-excluir-proposta');
        
        if (btnEditar) {
            const proposta = JSON.parse(btnEditar.closest('tr').dataset.proposta);
            preencherFormularioProposta(proposta);
        }
        if (btnExcluir) {
            const id = btnExcluir.dataset.id;
            if (confirm(`Tem certeza que deseja excluir a proposta ID ${id}?`)) {
                try {
                    const response = await fetch(`/api/propostas/excluir/${id}`, { method: 'DELETE' });
                    const resultado = await response.json();
                    if (!resultado.success) throw new Error(resultado.message);
                    alert(resultado.message);
                    dispararPesquisa();
                } catch (error) { alert(`Erro: ${error.message}`); }
            }
        }
    });
    
    loginButton.addEventListener('click', async () => {
        const username = document.getElementById('username').value;
        const password = passwordInput.value;
        try {
            const response = await fetch('/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username, password }) });
            const data = await response.json();
            if (data.success) {
                loginArea.style.display = 'none'; 
                mainContent.style.display = 'block';
                await Promise.all([
                    popularSelect(document.getElementById('prop-fabricante'), '/api/dados/fabricantes', 'Todos'),
                    popularSelect(document.getElementById('prop-categoria'), '/api/dados/categorias', 'Todas'),
                    popularSelect(document.getElementById('prop-cor'), '/api/dados/cores', 'Todas'),
                    popularSelect(document.getElementById('prop-pessoa'), '/api/clientes/listar-nomes', 'Selecione')
                ]);
                configurarGatilhosPesquisa();
                dispararPesquisa();
            } else { 
                document.getElementById('login-message').textContent = data.message;
            }
        } catch (error) { 
            document.getElementById('login-message').textContent = "Erro de conexão com o servidor.";
        }
    });

    passwordInput.addEventListener('keyup', (event) => { if (event.key === "Enter") loginButton.click(); });
});